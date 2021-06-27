from fastapi import FastAPI, HTTPException

from backend.RRD_parse import RRD_parser
import os
rrd_rest = FastAPI()


@rrd_rest.get(
    "/",
    summary="Get the data from a RRD file, takes in a rrd file path"
    )
async def get_rrd(rrd_path: str):
    is_file = os.path.isfile(rrd_path)
    if is_file:
        try:
            rr = RRD_parser(rrd_file=rrd_path)
            r = rr.compile_result()
            return r
        except Exception as e:
            HTTPException(status_code=500, detail=f"{e}")
    raise HTTPException(status_code=404, detail="RRD not found")
