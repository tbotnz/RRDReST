import subprocess
import xmltodict
import json
import re
from collections import defaultdict
from itertools import chain

class RRD_parser:

    def __init__(self, rrd_file):
        self.rrd_file = rrd_file
        self.ds = None
        self.step = None

    def get_data_source(self):
        STEP_VAL = None
        DS_VALS = []

        result = subprocess.check_output(f"rrdtool info {self.rrd_file}", shell=True).decode('utf-8')

        temp_arr = result.split("\n")

        for line in temp_arr:
            if " = " in line:
                raw_key = line.split(" = ")[0]
                raw_val = line.split(" = ")[1]
            
            if raw_key == "step":
                STEP_VAL = raw_val

            if ("ds[" in raw_key) and ("]." in raw_key):
                match_obj = re.match( r'^ds\[(.*)\]', raw_key)
                if match_obj:
                    ds_val = match_obj.group(1)
                    if ds_val not in DS_VALS:
                        DS_VALS.append(ds_val)
        self.step = STEP_VAL
        self.ds = DS_VALS


    def get_rrd_json(self, ds):
        # JSON
        # DS = "OUTNUCASTPKTS"
        # step = "300"

        rrd_xport_command = f"rrdtool xport --step {self.step} DEF:data={self.rrd_file}:{ds}:AVERAGE XPORT:data:{ds}"

        result = subprocess.check_output(rrd_xport_command, shell=True).decode('utf-8')
        json_result = json.dumps(xmltodict.parse(result),indent=4)

        replace_val = "\""+ds+"\": "
        #replace v key
        temp_result_one = re.sub("\"v\": ",  replace_val, json_result)

        return json.loads(temp_result_one)

    def compile_result(self):
        self.get_data_source()
        STEP_VAL = self.step
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
            master_result["meta"]["start"] = r["xport"]["meta"]["start"]
            master_result["meta"]["step"] = r["xport"]["meta"]["step"]
            master_result["meta"]["end"] = r["xport"]["meta"]["end"]
            master_result["meta"]["rows"] = 0
            master_result["meta"]["data_sources"].append(r["xport"]["meta"]["legend"]["entry"])
            TEMP_DS = r["xport"]["meta"]["legend"]["entry"]

            for collectible in chain(master_result["data"], r["xport"]["data"]["row"]):
                collector[collectible["t"]].update(collectible.items())

        #combine objs
        combined_list = list(collector.values())
        master_result["data"] = combined_list
        return master_result

if __name__ == "__main__":

    RRD_file = "/opt/librenms/rrd/accr04lab/port-id10.rrd"
    rr = RRD_parser(rrd_file=RRD_file)
    r = rr.compile_result()
    print (r)
