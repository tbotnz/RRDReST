from fastapi import FastAPI, HTTPException

from backend.RRD_parse import RRD_parser

from typing import Optional

import os
rrd_rest = FastAPI(
    title="RRDReST",
    description="Makes RRD files API-able",
    version="0.2",
)


@rrd_rest.get(
    "/",
    summary="Get the data from a RRD file, takes in a rrd file path"
    )
async def get_rrd(rrd_path: str, epoch_start_time: Optional[int] = None, epoch_end_time: Optional[int] = None):
    is_file = os.path.isfile(rrd_path)
    if is_file:
        if (epoch_start_time and not epoch_end_time) or (epoch_end_time and not epoch_start_time):
            raise HTTPException(status_code=500, detail="If epoch start or end time is specified both start and end time MUST be specified")
        try:
            rr = RRD_parser(
                            rrd_file=rrd_path,
                            start_time=epoch_start_time,
                            end_time=epoch_end_time
                            )
            r = rr.compile_result()
            return r
        except Exception as e:
            HTTPException(status_code=500, detail=f"{e}")
    raise HTTPException(status_code=404, detail="RRD not found")
