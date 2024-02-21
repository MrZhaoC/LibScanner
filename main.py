import argparse
import sys

# 引入ATVHunter

# parser = argparse.ArgumentParser(prog="ATVHunter")
# parser = argparse.ArgumentParser(usage="python main.py --apk apk_path")
parser = argparse.ArgumentParser(description="ATVHunter is an automatic tool for Android library detection.")
parser.add_argument('-a', '--apk', type=str, required=True, help="input apk path")
parser.add_argument('apk_path')

try:
    args = parser.parse_args()
except:
    parser.print_help()
    sys.exit(0)
apk_path = args.apk
apk_analysis = ATVHunter(apk_path)
apk_analysis.compare_core_feature()
