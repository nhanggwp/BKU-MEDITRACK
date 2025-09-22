"""
Drug Name to SMILES Conversion Service
Uses PubChem API to convert drug names to SMILES format
"""
import requests
import asyncio
import aiohttp
from typing import Optional, Dict, List, Tuple
import logging
import time
from functools import lru_cache

logger = logging.getLogger(__name__)


class DrugLookupService:
    """
    Service to convert drug names to SMILES format using PubChem API
    """
    
    def __init__(self, cache_size: int = 1000):
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.cache_size = cache_size
        
    @lru_cache(maxsize=1000)
    def get_smiles_sync(self, drug_name: str) -> Optional[str]:
        """
        Convert drug name to SMILES format using PubChem API (synchronous)
        
        Args:
            drug_name: Name of the drug
            
        Returns:
            SMILES string if found, None otherwise
        """
        try:
            # Clean up drug name
            clean_name = drug_name.strip().replace(" ", "%20")
            
            # First try to get compound ID by name
            url = f"{self.base_url}/compound/name/{clean_name}/cids/JSON"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Could not find compound for drug name: {drug_name}")
                return None
                
            data = response.json()
            if "IdentifierList" not in data or "CID" not in data["IdentifierList"]:
                logger.warning(f"No CID found for drug name: {drug_name}")
                return None
                
            cid = data["IdentifierList"]["CID"][0]
            
            # Get SMILES using CID - try multiple SMILES types
            smiles_url = f"{self.base_url}/compound/cid/{cid}/property/CanonicalSMILES,IsomericSMILES,ConnectivitySMILES/JSON"
            smiles_response = requests.get(smiles_url, timeout=10)
            
            if smiles_response.status_code != 200:
                logger.warning(f"Could not get SMILES for CID {cid}")
                return None
                
            smiles_data = smiles_response.json()
            if "PropertyTable" not in smiles_data or "Properties" not in smiles_data["PropertyTable"]:
                logger.warning(f"No SMILES data found for CID {cid}")
                return None
                
            properties = smiles_data["PropertyTable"]["Properties"][0]
            
            # Try different SMILES types in order of preference
            smiles = None
            for smiles_type in ["CanonicalSMILES", "IsomericSMILES", "ConnectivitySMILES"]:
                if smiles_type in properties:
                    smiles = properties[smiles_type]
                    break
                    
            if not smiles:
                logger.warning(f"No SMILES found in response for CID {cid}")
                return None
            logger.info(f"Successfully converted '{drug_name}' to SMILES: {smiles}")
            return smiles
            
        except Exception as e:
            logger.error(f"Error converting drug name '{drug_name}' to SMILES: {e}")
            return None
    
    async def get_smiles_async(self, drug_name: str, session: aiohttp.ClientSession) -> Optional[str]:
        """
        Convert drug name to SMILES format using PubChem API (asynchronous)
        
        Args:
            drug_name: Name of the drug
            session: aiohttp ClientSession
            
        Returns:
            SMILES string if found, None otherwise
        """
        try:
            # Clean up drug name
            clean_name = drug_name.strip().replace(" ", "%20")
            
            # First try to get compound ID by name
            url = f"{self.base_url}/compound/name/{clean_name}/cids/JSON"
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    logger.warning(f"Could not find compound for drug name: {drug_name}")
                    return None
                    
                data = await response.json()
                if "IdentifierList" not in data or "CID" not in data["IdentifierList"]:
                    logger.warning(f"No CID found for drug name: {drug_name}")
                    return None
                    
                cid = data["IdentifierList"]["CID"][0]
            
            # Get SMILES using CID - try multiple SMILES types
            smiles_url = f"{self.base_url}/compound/cid/{cid}/property/CanonicalSMILES,IsomericSMILES,ConnectivitySMILES/JSON"
            async with session.get(smiles_url, timeout=10) as smiles_response:
                if smiles_response.status != 200:
                    logger.warning(f"Could not get SMILES for CID {cid}")
                    return None
                    
                smiles_data = await smiles_response.json()
                if "PropertyTable" not in smiles_data or "Properties" not in smiles_data["PropertyTable"]:
                    logger.warning(f"No SMILES data found for CID {cid}")
                    return None
                    
                properties = smiles_data["PropertyTable"]["Properties"][0]
                
                # Try different SMILES types in order of preference
                smiles = None
                for smiles_type in ["CanonicalSMILES", "IsomericSMILES", "ConnectivitySMILES"]:
                    if smiles_type in properties:
                        smiles = properties[smiles_type]
                        break
                        
                if not smiles:
                    logger.warning(f"No SMILES found in response for CID {cid}")
                    return None
                logger.info(f"Successfully converted '{drug_name}' to SMILES: {smiles}")
                return smiles
                
        except Exception as e:
            logger.error(f"Error converting drug name '{drug_name}' to SMILES: {e}")
            return None
    
    async def get_smiles_batch_async(self, drug_names: List[str]) -> List[Tuple[str, Optional[str]]]:
        """
        Convert multiple drug names to SMILES format asynchronously
        
        Args:
            drug_names: List of drug names
            
        Returns:
            List of tuples (drug_name, smiles) where smiles can be None if not found
        """
        async with aiohttp.ClientSession() as session:
            tasks = []
            for drug_name in drug_names:
                task = self.get_smiles_async(drug_name, session)
                tasks.append(task)
            
            # Add small delays to avoid overwhelming the API
            results = []
            for i, task in enumerate(tasks):
                if i > 0 and i % 5 == 0:  # Add delay every 5 requests
                    await asyncio.sleep(0.5)
                result = await task
                results.append(result)
            
            return list(zip(drug_names, results))
    
    def clear_cache(self):
        """Clear the LRU cache"""
        self.get_smiles_sync.cache_clear()
        
    def get_cache_info(self):
        """Get cache statistics"""
        return self.get_smiles_sync.cache_info()


# Global instance
drug_lookup_service = DrugLookupService()


# Convenience functions
def drug_name_to_smiles(drug_name: str) -> Optional[str]:
    """
    Convert a single drug name to SMILES format
    
    Args:
        drug_name: Name of the drug
        
    Returns:
        SMILES string if found, None otherwise
    """
    return drug_lookup_service.get_smiles_sync(drug_name)


async def drug_names_to_smiles_batch(drug_names: List[str]) -> List[Tuple[str, Optional[str]]]:
    """
    Convert multiple drug names to SMILES format
    
    Args:
        drug_names: List of drug names
        
    Returns:
        List of tuples (drug_name, smiles) where smiles can be None if not found
    """
    return await drug_lookup_service.get_smiles_batch_async(drug_names)