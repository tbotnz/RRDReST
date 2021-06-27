from fastapi import FastAPI
from typing import Optional

from backend.RRD_parse import RRD_parser

rrd_rest = FastAPI()


@rrd_rest.get(
    "/",
    summary="Get the data from a RRD file, takes in a rrd file path"
    )
async def get_rrd(rrd_path: str):
    rr = RRD_parser(rrd_file=rrd_path)
    r = rr.compile_result()
    return r
