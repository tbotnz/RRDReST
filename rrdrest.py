import os

from backend.RRD_parse import RRD_parser
from fastapi import FastAPI, HTTPException
from typing import Optional

rrd_rest = FastAPI(
    title="RRDReST",
    description="Makes RRD files API-able",
    version="0.3",
)


@rrd_rest.get(
    "/",
    summary="Get the data from a RRD file, takes in a rrd file path",
    description="Fetches the RRD file data for the specified time range (if provided). "
                "If epoch times are not provided, the last 24 hour of data will be fetched.",
    )
async def get_rrd(
    rrd_path: str,
    epoch_start_time: Optional[int] = None,
    epoch_end_time: Optional[int] = None,
    epoch_output: Optional[bool] = False,
    timeshift: Optional[str] = None,
):
    # Check if the file exists
    if not os.path.isfile(rrd_path):
        raise HTTPException(status_code=404, detail="RRD file not found")

    if (epoch_start_time and not epoch_end_time) or (epoch_end_time and not epoch_start_time):
            raise HTTPException(status_code=400, detail="If epoch start or end time is specified both start and end time MUST be specified")

    #try:
    rr = RRD_parser(
            rrd_file=rrd_path,
            start_time=epoch_start_time,
            end_time=epoch_end_time,
            epoch_output=epoch_output,
            timeshift=timeshift
    )
    result = rr.compile_result()
    return result
    #except Exception as e:
    #    raise HTTPException(status_code=500, detail=f"Error processing RRD file: {e}")
