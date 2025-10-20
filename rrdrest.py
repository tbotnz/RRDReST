from fastapi import FastAPI, HTTPException
from pydantic import Field

from backend.RRD_parse import RRD_parser
from __version__ import __version__

from typing import Optional, Annotated
import os

rrd_rest = FastAPI(
    title="RRDReST",
    description="Makes RRD files API-able",
    version=__version__,
)


def _validate_time_params(
    epoch_start_time: Optional[int], epoch_end_time: Optional[int]
):
    if (epoch_start_time and not epoch_end_time) or (
        epoch_end_time and not epoch_start_time
    ):
        raise HTTPException(
            status_code=400,
            detail="If epoch start or end time is specified both start and end time MUST be specified",
        )


def _parse_rrd_file(
    rrd_path: Annotated[
        str, Field(description="RRD file path", examples=["/path/to/file.rrd"])
    ],
    epoch_start_time: Optional[int],
    epoch_end_time: Optional[int],
):
    if not os.path.isfile(rrd_path):
        raise HTTPException(status_code=404, detail=f"RRD file not found: {rrd_path}")

    _validate_time_params(epoch_start_time, epoch_end_time)

    try:
        rr = RRD_parser(
            rrd_file=rrd_path, start_time=epoch_start_time, end_time=epoch_end_time
        )
        return rr.compile_result()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing RRD file: {e}")


@rrd_rest.get("/", summary="Get data from a RRD file, takes in a rrd file path")
async def get_rrd(
    rrd_path: str,
    epoch_start_time: Optional[int] = None,
    epoch_end_time: Optional[int] = None,
):
    return _parse_rrd_file(rrd_path, epoch_start_time, epoch_end_time)


@rrd_rest.post("/", summary="Get multiple RRD files, takes in a list of rrd file paths")
async def get_rrd_multiple(
    rrd_paths: list[
        Annotated[
            str, Field(description="RRD file path", examples=["/path/to/file.rrd"])
        ]
    ],
    epoch_start_time: Optional[int] = None,
    epoch_end_time: Optional[int] = None,
):
    results = []
    for rrd_path in rrd_paths:
        result = _parse_rrd_file(rrd_path, epoch_start_time, epoch_end_time)
        results.append({rrd_path: result})
    if not results:
        raise HTTPException(status_code=404, detail="No RRD Data Found")
    return results
