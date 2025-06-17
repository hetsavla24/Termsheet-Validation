from mongodb_models import *
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio

class MongoMetricsCalculator:
    """Calculate various metrics for the dashboard using MongoDB"""
    
    async def calculate_user_metrics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate user-related metrics"""
        if user_id:
            total_users = 1 if await User.find_one(User.id == user_id) else 0
            active_users = 1 if await User.find_one({"$and": [{"id": user_id}, {"is_active": True}]}) else 0
            verified_users = 1 if await User.find_one({"$and": [{"id": user_id}, {"is_verified": True}]}) else 0
        else:
            total_users = await User.count()
            active_users = await User.find(User.is_active == True).count()
            verified_users = await User.find(User.is_verified == True).count()
        
        # Users who logged in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        if user_id:
            user_obj = await User.find_one(User.id == user_id)
            recent_active_users = 1 if (user_obj and user_obj.last_login and user_obj.last_login >= thirty_days_ago) else 0
        else:
            recent_active_users = await User.find(User.last_login >= thirty_days_ago).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "recent_active_users": recent_active_users,
            "user_engagement_rate": (recent_active_users / total_users * 100) if total_users > 0 else 0
        }
    
    async def calculate_file_metrics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate file-related metrics"""
        if user_id:
            total_files = await UploadedFile.find(UploadedFile.user_id == user_id).count()
            completed_files = await UploadedFile.find({
                "$and": [
                    {"user_id": user_id},
                    {"processing_status": ProcessingStatus.COMPLETED}
                ]
            }).count()
            failed_files = await UploadedFile.find({
                "$and": [
                    {"user_id": user_id},
                    {"processing_status": ProcessingStatus.FAILED}
                ]
            }).count()
            processing_files = await UploadedFile.find({
                "$and": [
                    {"user_id": user_id},
                    {"processing_status": ProcessingStatus.PROCESSING}
                ]
            }).count()
        else:
            total_files = await UploadedFile.count()
            completed_files = await UploadedFile.find(UploadedFile.processing_status == ProcessingStatus.COMPLETED).count()
            failed_files = await UploadedFile.find(UploadedFile.processing_status == ProcessingStatus.FAILED).count()
            processing_files = await UploadedFile.find(UploadedFile.processing_status == ProcessingStatus.PROCESSING).count()
        
        # Calculate average file size
        pipeline = [
            {"$group": {"_id": None, "avg_size": {"$avg": "$file_size"}}}
        ]
        result = await UploadedFile.aggregate(pipeline).to_list(1)
        avg_file_size = result[0]["avg_size"] if result else 0
        
        # Average processing time for completed files
        pipeline = [
            {"$match": {"processing_status": ProcessingStatus.COMPLETED, "processing_time": {"$ne": None}}},
            {"$group": {"_id": None, "avg_time": {"$avg": "$processing_time"}}}
        ]
        result = await UploadedFile.aggregate(pipeline).to_list(1)
        avg_processing_time = result[0]["avg_time"] if result else 0
        
        # Files uploaded in last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_uploads = await UploadedFile.find(UploadedFile.upload_timestamp >= seven_days_ago).count()
        
        return {
            "total_files": total_files,
            "completed_files": completed_files,
            "failed_files": failed_files,
            "processing_files": processing_files,
            "success_rate": (completed_files / total_files * 100) if total_files > 0 else 0,
            "average_file_size_mb": round(avg_file_size / (1024 * 1024), 2) if avg_file_size else 0,
            "average_processing_time": round(avg_processing_time, 2) if avg_processing_time else 0,
            "recent_uploads": recent_uploads
        }
    
    async def calculate_validation_metrics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate validation session metrics"""
        query_filter = {"user_id": user_id} if user_id else {}
        
        total_sessions = await ValidationSession.find(query_filter).count()
        completed_sessions = await ValidationSession.find({
            **query_filter,
            "status": ProcessingStatus.COMPLETED
        }).count()
        failed_sessions = await ValidationSession.find({
            **query_filter,
            "status": ProcessingStatus.FAILED
        }).count()
        active_sessions = await ValidationSession.find({
            **query_filter,
            "status": ProcessingStatus.PROCESSING
        }).count()
        
        # Average accuracy score
        pipeline = [
            {"$match": {"accuracy_score": {"$ne": None}}},
            {"$group": {"_id": None, "avg_accuracy": {"$avg": "$accuracy_score"}}}
        ]
        result = await ValidationSession.aggregate(pipeline).to_list(1)
        avg_accuracy = result[0]["avg_accuracy"] if result else 0
        
        # Average processing time
        pipeline = [
            {"$match": {"processing_time": {"$ne": None}}},
            {"$group": {"_id": None, "avg_time": {"$avg": "$processing_time"}}}
        ]
        result = await ValidationSession.aggregate(pipeline).to_list(1)
        avg_validation_time = result[0]["avg_time"] if result else 0
        
        # Sessions in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_sessions = await ValidationSession.find({
            **query_filter,
            "created_at": {"$gte": thirty_days_ago}
        }).count()
        
        # Compliance status distribution
        pipeline = [
            {"$match": {"compliance_status": {"$ne": None}}},
            {"$group": {"_id": "$compliance_status", "count": {"$sum": 1}}}
        ]
        compliance_results = await ValidationSession.aggregate(pipeline).to_list(100)
        compliance_distribution = {result["_id"]: result["count"] for result in compliance_results}
        
        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "failed_sessions": failed_sessions,
            "active_sessions": active_sessions,
            "success_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            "average_accuracy": round(avg_accuracy * 100, 2) if avg_accuracy else 0,
            "average_processing_time": round(avg_validation_time, 2) if avg_validation_time else 0,
            "recent_sessions": recent_sessions,
            "compliance_distribution": compliance_distribution
        }
    
    async def calculate_template_metrics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate template-related metrics"""
        query_filter = {"created_by": user_id} if user_id else {}
        
        total_templates = await MasterTemplate.find(query_filter).count()
        active_templates = await MasterTemplate.find({
            **query_filter,
            "is_active": True
        }).count()
        
        # Most used template
        most_used = await MasterTemplate.find(query_filter).sort(-MasterTemplate.usage_count).first()
        
        # Templates used in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recently_used = await MasterTemplate.find({
            **query_filter,
            "last_used": {"$gte": thirty_days_ago}
        }).count()
        
        # Average usage count
        pipeline = [
            {"$group": {"_id": None, "avg_usage": {"$avg": "$usage_count"}}}
        ]
        if user_id:
            pipeline.insert(0, {"$match": {"created_by": user_id}})
        
        result = await MasterTemplate.aggregate(pipeline).to_list(1)
        avg_usage = result[0]["avg_usage"] if result else 0
        
        return {
            "total_templates": total_templates,
            "active_templates": active_templates,
            "most_used_template": {
                "name": most_used.template_name if most_used else None,
                "usage_count": most_used.usage_count if most_used else 0
            },
            "recently_used_templates": recently_used,
            "average_usage_count": round(avg_usage, 2) if avg_usage else 0
        }
    
    async def calculate_dashboard_summary(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate comprehensive dashboard summary"""
        user_metrics, file_metrics, validation_metrics, template_metrics = await asyncio.gather(
            self.calculate_user_metrics(user_id),
            self.calculate_file_metrics(user_id),
            self.calculate_validation_metrics(user_id),
            self.calculate_template_metrics(user_id)
        )
        
        return {
            "overview": {
                "total_users": user_metrics["total_users"],
                "total_files": file_metrics["total_files"],
                "total_sessions": validation_metrics["total_sessions"],
                "total_templates": template_metrics["total_templates"]
            },
            "performance": {
                "file_success_rate": file_metrics["success_rate"],
                "validation_success_rate": validation_metrics["success_rate"],
                "average_accuracy": validation_metrics["average_accuracy"],
                "average_processing_time": validation_metrics["average_processing_time"]
            },
            "activity": {
                "recent_uploads": file_metrics["recent_uploads"],
                "recent_sessions": validation_metrics["recent_sessions"],
                "active_sessions": validation_metrics["active_sessions"],
                "user_engagement_rate": user_metrics["user_engagement_rate"]
            },
            "detailed_metrics": {
                "users": user_metrics,
                "files": file_metrics,
                "validations": validation_metrics,
                "templates": template_metrics
            }
        }
    
    async def store_daily_metrics(self, date: Optional[datetime] = None):
        """Store daily aggregated metrics"""
        if not date:
            date = datetime.utcnow().date()
        
        # Calculate all metrics
        summary = await self.calculate_dashboard_summary()
        
        # Store key metrics
        metrics_to_store = [
            {
                "metric_name": "daily_total_users",
                "metric_value": float(summary["overview"]["total_users"]),
                "metric_type": "count",
                "period": "daily",
                "date": datetime.combine(date, datetime.min.time())
            },
            {
                "metric_name": "daily_total_files",
                "metric_value": float(summary["overview"]["total_files"]),
                "metric_type": "count",
                "period": "daily",
                "date": datetime.combine(date, datetime.min.time())
            },
            {
                "metric_name": "daily_total_sessions",
                "metric_value": float(summary["overview"]["total_sessions"]),
                "metric_type": "count",
                "period": "daily",
                "date": datetime.combine(date, datetime.min.time())
            },
            {
                "metric_name": "daily_validation_success_rate",
                "metric_value": summary["performance"]["validation_success_rate"],
                "metric_type": "percentage",
                "period": "daily",
                "date": datetime.combine(date, datetime.min.time())
            },
            {
                "metric_name": "daily_average_accuracy",
                "metric_value": summary["performance"]["average_accuracy"],
                "metric_type": "percentage",
                "period": "daily",
                "date": datetime.combine(date, datetime.min.time())
            }
        ]
        
        # Delete existing metrics for the date
        await DashboardMetrics.find({
            "date": datetime.combine(date, datetime.min.time()),
            "period": "daily"
        }).delete()
        
        # Insert new metrics
        metrics_objects = [DashboardMetrics(**metric_data) for metric_data in metrics_to_store]
        await DashboardMetrics.insert_many(metrics_objects)
    
    async def get_trend_data(self, metric_name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get trend data for a specific metric"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        trends = await DashboardMetrics.find({
            "metric_name": metric_name,
            "date": {"$gte": start_date},
            "period": "daily"
        }).sort("date").to_list(None)
        
        return [
            {
                "date": trend.date.isoformat(),
                "value": trend.metric_value,
                "type": trend.metric_type
            }
            for trend in trends
        ] 