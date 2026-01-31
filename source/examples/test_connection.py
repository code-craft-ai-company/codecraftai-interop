#!/usr/bin/env python3
"""
    Test script for DLI Power Rest Client.
    Prompts for password and attempts to connect to the device.
"""

import getpass
import sys
import logging

# Add the source directory to sys.path to ensure we pick up the local package
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../../../")))

from automojo.credentials.basiccredential import BasicCredential
from automojo.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient


def test_connection():
    # Setup basic logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    ip = "172.16.0.23"
    user = "admin"

    print(f"\n--- DLI Power REST Client Test ---")
    print(f"Target: {ip}")
    print(f"User:   {user}")
    
    try:
        password = getpass.getpass(f"Enter password for {user}: ")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return

    if not password:
        print("Password cannot be empty.")
        return

    print(f"\nConnecting to {ip}...")

    try:
        # Create credential
        cred = BasicCredential(identifier="test_cred", categories=["basic"], username=user, password=password)
        
        # Initialize client
        client = DliPowerRestClient(host=ip, credential=cred)
        
        # Test 1: Get Outlets (Relay Group)
        print("\n[Test 1] Retrieving Outlets...")
        outlets = client.relay.get_outlets()
        print(f"Success! Found {len(outlets)} outlets.")
        for i, outlet in enumerate(outlets):
            state_str = "ON" if outlet.state else "OFF"
            print(f"  Outlet {i}: {outlet.name:<20} [{state_str}]")

        # Test 1a: Cycle Outlets
        print("\n[Test 1a] Cycling Outlets (Off -> On)...")
        controls = client.relay.get_outlet_controls()
        
        if not controls:
            print("  No named outlet controls found to cycle.")
        
        import time
        for name, control in controls.items():
            print(f"  Cycling '{name}'...")
            print(f"    Turning OFF '{name}'")
            control.off()
            time.sleep(4)
            print(f"    Turning ON  '{name}'")
            control.on()
            print(f"    Done cycling '{name}'")
            time.sleep(4)

        # Test 2: Get Network Config (Network Group)
        print("\n[Test 2] Retrieving Network Configuration...")
        net_config = client.network.get_configuration()
        print("Success! Network config retrieved.")
        # Print a few interesting keys if present
        for key in ["hostname", "ip_address", "mac_address"]:
            if key in net_config:
                print(f"  {key}: {net_config[key]}")

        # Test 3: Get Meters (Meter Group)
        print("\n[Test 3] Retrieving Meters...")
        meters = client.meter.get_meters()
        print(f"Success! Found {len(meters)} meters.")
        for meter in meters:
            if meter.name and meter.value is not None:
                print(f"  {meter.name}: {meter.value}")

        print("\n--- Test Completed Successfully ---")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()
