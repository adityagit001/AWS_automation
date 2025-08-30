# app.py
import boto3
from botocore.exceptions import ClientError
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ---------------------- Launch Instance ----------------------
@app.route("/launch-instance", methods=["POST"])
def launch_instance():
    """Launch an EC2 instance with values provided by frontend."""
    try:
        data = request.get_json(force=True)

        region_name = data.get("region_name")       # e.g. "ap-south-1"
        image_id = data.get("image_id")             # e.g. "ami-0c4a668b99e68bbde"
        instance_type = data.get("instance_type")   # e.g. "t3.micro"
        key_name = data.get("key_name")             # e.g. "Adityakey"

        if not all([region_name, image_id, instance_type, key_name]):
            return jsonify({"error": "Missing required parameters"}), 400

        ec2 = boto3.resource("ec2", region_name=region_name)

        instances = ec2.create_instances(
            ImageId=image_id,
            MinCount=1,
            MaxCount=1,
            InstanceType=instance_type,
            KeyName=key_name
        )
        
        instance = instances[0]
        instance.wait_until_running()
        instance.load()

        return jsonify({
            "message": "Instance launched successfully",
            "instance_id": instance.id,
            "public_ip": instance.public_ip_address,
            "region": region_name,
            "state": instance.state["Name"]
        }), 200

    except ClientError as e:
        return jsonify({"error": str(e)}), 400


# ---------------------- Stop Instance ----------------------
@app.route("/stop-instance", methods=["POST"])
def stop_instance():
    """Stop an existing EC2 instance."""
    try:
        data = request.get_json(force=True)

        region_name = data.get("region_name")
        instance_id = data.get("instance_id")

        if not all([region_name, instance_id]):
            return jsonify({"error": "Missing required parameters"}), 400

        ec2 = boto3.resource("ec2", region_name=region_name)
        instance = ec2.Instance(instance_id)

        instance.stop()
        instance.wait_until_stopped()
        instance.load()

        return jsonify({
            "message": "Instance stopped successfully",
            "instance_id": instance.id,
            "region": region_name,
            "state": instance.state["Name"]
        }), 200

    except ClientError as e:
        return jsonify({"error": str(e)}), 400


# ---------------------- Terminate Instance ----------------------
@app.route("/terminate-instance", methods=["POST"])
def terminate_instance():
    """Terminate an existing EC2 instance."""
    try:
        data = request.get_json(force=True)

        region_name = data.get("region_name")
        instance_id = data.get("instance_id")

        if not all([region_name, instance_id]):
            return jsonify({"error": "Missing required parameters"}), 400

        ec2 = boto3.resource("ec2", region_name=region_name)
        instance = ec2.Instance(instance_id)

        instance.terminate()
        instance.wait_until_terminated()
        instance.load()

        return jsonify({
            "message": "Instance terminated successfully",
            "instance_id": instance.id,
            "region": region_name,
            "state": instance.state["Name"]
        }), 200

    except ClientError as e:
        return jsonify({"error": str(e)}), 400


# ---------------------- Health Check ----------------------
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "Backend is running"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
