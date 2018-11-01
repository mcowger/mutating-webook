from flask import Flask, request, jsonify
from pprint import pprint
import json
import jsonpatch
import copy
import base64

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    allowed = True
    request_info = request.json
    modified_spec = copy.deepcopy(request_info)

    print(request.data)

    # pprint(request_info)
    for container_spec in modified_spec["request"]["object"]["spec"]["containers"]:
        print("Processing container: {}/{}".format(
            modified_spec["request"]["object"]["metadata"]["name"],
            container_spec['name']
        )
        )
        fixup_image(container_spec)

    print("Diffing original request to modified request and generating JSONPatch")

    patch = jsonpatch.JsonPatch.from_diff(request_info, modified_spec)
    print("JSON Patch:")

    print()
    print(str(patch))

    admission_response = {
        "allowed": True,
        "uid": request_info["request"]["uid"],
        "patch": base64.b64encode(str(patch).encode()).decode(),
        "patchtype": "JSONPatch"
    }
    admissionReview = {
        "response": admission_response
    }
    print("Sending Response to K8S:")
    print(admissionReview)
    return jsonify(admissionReview)


def fixup_image(container_spec):
    print("Fixing up container spec for {}".format(container_spec["name"]))
    if "redis" in container_spec["image"]:
        print("Found redis in image name - fixing")
        container_spec["image"] = "tmo/notredis"


app.run(host='0.0.0.0', debug=True)
