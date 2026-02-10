#include <memory>
#include <utility>
#include <vector>

#include <Eigen/Core>

// Patchwork++-ROS
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <rclcpp/qos.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <std_msgs/msg/string.hpp>

#include "GroundSegmentationServer.hpp"
#include "Utils.hpp"

namespace patchworkpp_ros {

using utils::EigenToPointCloud2;
using utils::GetTimestamps;
using utils::PointCloud2ToEigen;

GroundSegmentationServer::GroundSegmentationServer(const rclcpp::NodeOptions &options)
    : rclcpp::Node("patchworkpp_node", options),
      filter_high_z_(declare_parameter<bool>("filter_high_z", true)),
      th_filter_high_z_(declare_parameter<float>("th_filter_high_z", 0.5)) {
  patchwork::Params params;
  base_frame_ = declare_parameter<std::string>("base_frame", base_frame_);

  params.sensor_height = declare_parameter<double>("sensor_height", params.sensor_height);
  params.num_iter      = declare_parameter<int>("num_iter", params.num_iter);
  params.num_lpr       = declare_parameter<int>("num_lpr", params.num_lpr);
  params.num_min_pts   = declare_parameter<int>("num_min_pts", params.num_min_pts);
  params.th_seeds      = declare_parameter<double>("th_seeds", params.th_seeds);

  params.th_dist    = declare_parameter<double>("th_dist", params.th_dist);
  params.th_seeds_v = declare_parameter<double>("th_seeds_v", params.th_seeds_v);
  params.th_dist_v  = declare_parameter<double>("th_dist_v", params.th_dist_v);

  params.max_range       = declare_parameter<double>("max_range", params.max_range);
  params.min_range       = declare_parameter<double>("min_range", params.min_range);
  params.uprightness_thr = declare_parameter<double>("uprightness_thr", params.uprightness_thr);

  params.verbose = get_parameter<bool>("verbose", params.verbose);

  // ToDo. Support intensity
  params.enable_RNR = false;

  // Construct the main Patchwork++ node
  Patchworkpp_ = std::make_unique<patchwork::PatchWorkpp>(params);

  // Initialize subscribers
  pointcloud_sub_ = create_subscription<sensor_msgs::msg::PointCloud2>(
      "pointcloud_topic",
      rclcpp::SensorDataQoS(),
      std::bind(&GroundSegmentationServer::EstimateGround, this, std::placeholders::_1));

  /*
   * We use the following QoS setting for reliable ground segmentation.
   * If you want to run Patchwork++ in real-time and real-world operation,
   * please change the QoS setting
   */
  //  rclcpp::QoS qos((rclcpp::SystemDefaultsQoS().keep_last(1).durability_volatile()));
  rclcpp::QoS qos(rclcpp::QoSInitialization::from_rmw(rmw_qos_profile_default));
  qos.reliability(RMW_QOS_POLICY_RELIABILITY_RELIABLE);
  qos.durability(RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL);
  nonground_publisher_ =
      create_publisher<sensor_msgs::msg::PointCloud2>("/patchworkpp/nonground", qos);

  RCLCPP_INFO(this->get_logger(), "Patchwork++ ROS 2 node initialized");
}

void GroundSegmentationServer::EstimateGround(
    const sensor_msgs::msg::PointCloud2::ConstSharedPtr &msg) {
  auto cloud = patchworkpp_ros::utils::PointCloud2ToEigenMat(msg);

  // Filter points higher than a certain threshold if the option is enabled
  if (filter_high_z_) {
    auto mask = cloud.col(2).array() < th_filter_high_z_;
    int count = mask.count();
    Eigen::MatrixXf filtered(count, 3);
    int idx = 0;
    for (int i = 0; i < cloud.rows(); i++) {
        if (mask(i)) {
            filtered.row(idx++) = cloud.row(i);
        }
    }
    cloud = filtered;
  }

  // Estimate ground
  Patchworkpp_->estimateGround(cloud);
  Eigen::MatrixX3f nonground = Patchworkpp_->getNonground();

//   // Filter points higher than a certain threshold if the option is enabled
//   if (filter_high_z_) {
//     auto mask = nonground.col(2).array() < th_filter_high_z_;
//     int count = mask.count();
//     Eigen::MatrixXf filtered(count, 3);
//     int idx = 0;
//     for (int i = 0; i < nonground.rows(); i++) {
//         if (mask(i)) {
//             filtered.row(idx++) = nonground.row(i);
//         }
//     }
//     nonground = filtered;
//   }
  std_msgs::msg::Header header = msg->header;
  header.frame_id              = base_frame_;
  nonground_publisher_->publish(
      std::move(patchworkpp_ros::utils::EigenMatToPointCloud2(nonground, header)));
  double time_taken          = Patchworkpp_->getTimeTaken();
}


}  // namespace patchworkpp_ros

#include "rclcpp_components/register_node_macro.hpp"
RCLCPP_COMPONENTS_REGISTER_NODE(patchworkpp_ros::GroundSegmentationServer)
