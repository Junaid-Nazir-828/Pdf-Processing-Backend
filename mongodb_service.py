from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import constant

class MongoDBService:
    def __init__(self):
        # Get MongoDB connection details from environment variables
        mongo_uri = constant.MONGODB_URI
        db_name = constant.MONGODB_DB_NAME
        
        # Connect to MongoDB
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.users = self.db["User"]
        self.analyses = self.db["Analysis"]
    
    def get_all_users(self):
        """
        Get all user records from the users collection
        
        Returns:
            list: List of all user documents
        """
        try:
            results = list(self.users.find())
            # for i in results:
            #     print(i)
            print(results)
            # return results
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
        
    def update_analysis_status(self, analysis_id, status):
        """
        Update the status of an analysis
        
        Args:
            analysis_id (str): The ID of the analysis
            status (str): The new status ("PENDING", "PROCESSING", "COMPLETED", "FAILED")
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert string ID to ObjectId if needed
            doc_id = ObjectId(analysis_id) if not isinstance(analysis_id, ObjectId) else analysis_id
            
            result = self.analyses.update_one(
                {"_id": doc_id},
                {
                    "$set": {
                        "status": status,
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating analysis status: {e}")
            return False
    
    def update_analysis_results(self, analysis_id, extracted_texts, status="COMPLETED"):
        """
        Update the results and status of an analysis
        
        Args:
            analysis_id (str): The ID of the analysis
            extracted_texts (list): List of extracted text objects with page numbers
            status (str): The new status (default: "COMPLETED")
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert string ID to ObjectId if needed
            doc_id = ObjectId(analysis_id) if not isinstance(analysis_id, ObjectId) else analysis_id
            
            result = self.analyses.update_one(
                {"_id": doc_id},
                {
                    "$set": {
                        "status": status,
                        "result": extracted_texts,
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating analysis results: {e}")
            return False
    
    def get_analysis(self, analysis_id):
        """
        Get analysis details by ID
        
        Args:
            analysis_id (str): The ID of the analysis
            
        Returns:
            dict: Analysis document or None if not found
        """
        try:
            # Convert string ID to ObjectId if needed
            doc_id = ObjectId(analysis_id) if not isinstance(analysis_id, ObjectId) else analysis_id
            
            return self.analyses.find_one({"_id": doc_id})
        except Exception as e:
            print(f"Error getting analysis: {e}")
            return None
    
    def close_connection(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()

