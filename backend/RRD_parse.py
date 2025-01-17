import datetime
import json
import pytz
import re
import subprocess
import xmltodict

from collections import defaultdict
from itertools import chain


class RRD_parser:

    def __init__(self, rrd_file=None, start_time=None, end_time=None, epoch_output=False):
        self.rrd_file = rrd_file
        self.ds = None
        self.step = None
        if epoch_output:
            self.time_format = "%s"
        else:
            self.time_format = "%Y-%m-%d %H:%M:%S"
        self.check_dependc()
        self.start_time = start_time
        self.end_time = end_time

    def check_dependc(self):
        result = subprocess.check_output(
            "rrdtool --version",
            shell=True
        ).decode('utf-8')
        if "RRDtool 1." not in result:
            raise Exception("RRDtool version not found, check rrdtool installed")

    def get_data_source(self):
        """ gets datasources from rrd tool """

        STEP_VAL = None
        DS_VALS = []

        result = subprocess.check_output(
            f"rrdtool info {self.rrd_file}",
            shell=True
            ).decode('utf-8')

        temp_arr = result.split("\n")

        for line in temp_arr:
            if " = " in line:
                raw_key = line.split(" = ")[0]
                raw_val = line.split(" = ")[1]

            if raw_key == "step":
                STEP_VAL = raw_val

            if ("ds[" in raw_key) and ("]." in raw_key):
                match_obj = re.match(r'^ds\[(.*)\]', raw_key)
                if match_obj:
                    ds_val = match_obj.group(1)
                    if ds_val not in DS_VALS:
                        DS_VALS.append(ds_val)
        self.step = STEP_VAL
        self.ds = DS_VALS

    def get_rrd_json(self, ds):
        """ gets RRD json from rrd tool """
        
        rrd_xport_command = f"rrdtool xport --step {self.step} DEF:data={self.rrd_file}:{ds}:AVERAGE XPORT:data:{ds} --showtime"
        if self.start_time:
            rrd_xport_command = f"rrdtool xport DEF:data={self.rrd_file}:{ds}:AVERAGE XPORT:data:{ds} --showtime --start {self.start_time} --end {self.end_time}"
        result = subprocess.check_output(
            rrd_xport_command,
            shell=True
        ).decode('utf-8')
        json_result = json.dumps(xmltodict.parse(result), indent=4)
        # replace rrdtool v key with the ds
        replace_val = "\""+ds.lower()+"\": "
        temp_result_one = re.sub("\"v\": ",  replace_val, json_result)
        return json.loads(temp_result_one)

    def cleanup_payload(self, payload):
        """ cleans up / transforms response payload """

        # convert timezones and floats
        for count, temp_obj in enumerate(payload["data"]):
            epoch_time = temp_obj["t"]
            # Convert the epoch time to UTC
            utc_time = datetime.datetime.fromtimestamp(
                int(epoch_time), tz=pytz.utc
            ).strftime(self.time_format)
            payload["data"][count]["t"] = utc_time
            for key in payload["data"][count]:
                temp_val = ""
                if "e+" in payload["data"][count][key] or "e-" in payload["data"][count][key]:
                    temp_val = payload["data"][count][key]
                    payload["data"][count][key] = float(temp_val)
        pl = json.dumps(payload)

        # convert ints, floats
        pl = re.sub(r'\"(\d+)\"', r'\1', f"{pl}")
        pl = re.sub(r'\"(\d+\.\d+)\"', r'\1', f"{pl}")

        # convert NaN to null
        pl = re.sub(r'\"NaN\"', "null", f"{pl}")

        # replace "t" with time
        pl = re.sub(r'\"t\"', r'"time"', f"{pl}")

        # return response as JSON obj
        return json.loads(pl)

    def compile_result(self):
        self.get_data_source()
        DS_VALUES = self.ds
        master_result = {
            "meta": {
                "start": "",
                "step": "",
                "end": "",
                "rows": "",
                "data_sources": []
            },
            "data": [],

        }

        collector = defaultdict(dict)

        for d in DS_VALUES:
            r = self.get_rrd_json(ds=d)
            master_result["meta"]["start"] = datetime.datetime.fromtimestamp(
                int(r["xport"]["meta"]["start"])
                ).strftime(self.time_format)
            master_result["meta"]["step"] = r["xport"]["meta"]["step"]
            master_result["meta"]["end"] = datetime.datetime.fromtimestamp(
                int(r["xport"]["meta"]["end"])
                ).strftime(self.time_format)
            master_result["meta"]["rows"] = 0
            master_result["meta"]["data_sources"].append(
                r["xport"]["meta"]["legend"]["entry"]
                )

            for collectible in chain(
                master_result["data"], r["xport"]["data"]["row"]
                                    ):
                collector[collectible["t"]].update(collectible.items())

        # combine objs, add row_count
        combined_list = list(collector.values())
        master_result["data"] = combined_list
        master_result["meta"]["rows"] = len(combined_list)
        final_result = self.cleanup_payload(master_result)
        return final_result


# if __name__ == "__main__":
#     RRD_file = "sensor-voltage-cisco-entity-sensor-532.rrd"
#     rr = RRD_parser(rrd_file=RRD_file)
#     r = rr.compile_result()
#     print (r)
