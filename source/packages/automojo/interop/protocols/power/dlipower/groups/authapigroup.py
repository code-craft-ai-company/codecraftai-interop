"""
    .. module:: apinodeauth
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: apinodeauth module.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import List, Optional, TYPE_CHECKING

import json
import requests


from automojo.restclient.base.aspectsrest import AspectsRest
from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.interop.protocols.power.dlipower.responsemodel import User


if TYPE_CHECKING:
    from automojo.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient

class AuthApiGroup(RestApiGroup):
    """
        Interface layer for REST operations on authentication.
    """
    
    def get_users(self, aspects: Optional[AspectsRest] = None) -> List[User]:
        """
            Retrieves the list of users from the power controller.
            
            :param aspects: Optional REST call aspects configuration.
            
            :returns: List of :class:`User` objects.
        """
        leaf = "restapi/auth/users/"
        client: "DliPowerRestClient" = self.client
        
        # We need to use recursion/depth or specific query to get full objects?
        # The spec says generic GET to collection returns list of references?
        # Example 258: Add user returns representation.
        # Example 253: Matrix URI to get specific fields.
        
        # To get all users with details, we probably need deeper query or iterate.
        # But let's try a basic GET first. 
        # Actually, to get full representation of children, we might need depth.
        # Reference line 173: Range: dli-depth=1
        
        # Let's assume we want to get the list of users.
        # The spec example 276 shows getting indices.
        
        # For now, let's implement a method that lists user names or full objects if possible.
        # The spec implies we might get a list of links if we just GET the collection.
        
        # We can use matrix URI "all" to get all.
        leaf = "restapi/auth/users/all/"
        
        leaf = "restapi/auth/users/all/" 
        client: "DliPowerRestClient" = self.client
        
        resp: requests.Response = client.perform_call(leaf=leaf, method="GET", params=None, body=None, exp_status=[200, 207], aspects=aspects)
        
        data = resp.json()
        
        users = []
        if isinstance(data, list):
            for u_data in data:
                # Need to map fields manually or blindly pass
                # Note: User dataclass has specific fields. 
                # API returns JSON.
                if isinstance(u_data, dict):
                    users.append(User(
                        name=u_data.get("name"),
                        is_allowed=u_data.get("is_allowed"),
                        is_admin=u_data.get("is_admin", False), # Defaulting
                        outlet_access=u_data.get("outlet_access", []),
                        password=None # Password usually not returned
                    ))
        
        return users

    def create_user(self, user: User, aspects: Optional[AspectsRest] = None) -> User:
        """
            Creates a new user.
            
            :param user: The user object to create.
            :param aspects: Optional REST call aspects configuration.
            
            :returns: The created user object returned by the server.
        """
        leaf = "restapi/auth/users/"
        client: "DliPowerRestClient" = self.client
        
        payload = {
            "name": user.name,
            "password": user.password,
            "is_allowed": user.is_allowed,
            "outlet_access": user.outlet_access
        }
        # is_admin cannot be set on creation? Spec doesn't explicitly say but example 260 doesn't show it.
        # Actually example 260 maps input data.
        if user.is_admin:
             payload["is_admin"] = user.is_admin

        headers = {"Prefer": "return=representation", "Content-Type": "application/json"}
        body_content = json.dumps(payload)
        
        resp: requests.Response = client.perform_call(leaf=leaf, method="POST", params=None, body=body_content, headers=headers, exp_status=201, aspects=aspects)
        
        u_data = resp.json()
        rtnval = User(
            name=u_data.get("name"),
            is_allowed=u_data.get("is_allowed"),
            is_admin=u_data.get("is_admin", False),
            outlet_access=u_data.get("outlet_access", []),
            password=None
        )
        return rtnval

    def delete_user(self, username: str, aspects: Optional[AspectsRest] = None) -> bool:
        """
            Deletes a user.
            
            :param username: The name of the user to delete.
            :param aspects: Optional REST call aspects configuration.
        """
        # Using matrix URI for idempotency as suggested in section 7.2
        leaf = f"restapi/auth/users/name={username}/"
        client: "DliPowerRestClient" = self.client
        
        client.perform_call(leaf=leaf, method="DELETE", params=None, body=None, exp_status=[200, 204], aspects=aspects)
        return True

    def change_password(self, username: str, new_password: str, old_password: Optional[str] = None, aspects: Optional[AspectsRest] = None) -> bool:
        """
            Changes a user's password.
            
            :param username: The user to update.
            :param new_password: The new password.
            :param old_password: The old password (optional).
            :param aspects: Optional REST call aspects configuration.
        """
        leaf = f"restapi/auth/users/name={username}/"
        client: "DliPowerRestClient" = self.client
        
        data = {"password": new_password}
        if old_password:
             data["old_password"] = old_password
             
        headers = {"Content-Type": "application/json"}
        body_content = json.dumps(data)
             
        client.perform_call(leaf=leaf, method="PATCH", params=None, body=body_content, headers=headers, exp_status=[200, 204], aspects=aspects)
        return True
