import traceback
from typing import Any,  Optional

from mcp.server.fastmcp import FastMCP
import logging
import requests


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Initialize FastMCP server
mcp = FastMCP("mcc-mcp")

def format_dataset(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature

    logger.debug(props.concept_id())

    try:
        return f"""
ConceptID: {props.concept_id()}
Description: {props.abstract()}
Shortname: {props.summary()['short-name']}
"""
    except Exception as e:
        logging.error(traceback.format_exc())
        #Currently an error in earthaccess that relies on `FileDistributionInformation` to exist will be caught here from the 'summary()' method. 
        # Returning empty string.
        return ""


@mcp.tool()
async def check_compliance(
    
    file_path: str,
    compliance: str= "CF",
    compliance_version: str="1.7") -> str:
    """Check the compliance of a file against the MCC

    Args:
        filepath: (Required) Location on the local filesystem of the file to upload
        compliance: (Required) The compliance checks to run (e.g. CF, GDS2)
        compliance_version: (Required) The version of the given compliance to use. (e.g. 1.7)

    """
    args = {}
    if file_path is not None:
         args['file_path'] = file_path
    if compliance is not None:
         args['compliance'] = compliance
    if compliance_version is not None:
         args['compliance_version'] = compliance_version

    try:
        # curl -L -F CF=on -F CF-version=1.7 -F file-upload=@20020901090000-JPL-L4_GHRSST-SSTfnd-MUR25-GLOB-v02.0-fv04.2.nc -F response=json https://mcc.podaac.earthdatacloud.nasa.gov/check 
        print("making request")
        url = "https://mcc.podaac.earthdatacloud.nasa.gov/check"
        form_data = {compliance:"on", "CF-version": compliance_version, "response":"json"}
        resp = requests.post(url, data=form_data, files={'file-upload': open(file_path, 'rb')}, allow_redirects=True)
        
    except:
        print("error!")

    logger.debug(len(resp.json()))
    
    #alerts = [format_dataset(feature) for feature in data["features"]]
    return resp.json()


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
