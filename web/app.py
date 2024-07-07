from web.page import demo
import argparse

args = argparse.ArgumentParser()
args.add_argument("--port", type=int, default=7005)
args = args.parse_args()

demo.launch(
    # server_name="0.0.0.0",
    server_port=args.port
)



