import btc_wallet.menus
import argparse
from btc_wallet.util import Modes

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--mode", metavar='m',type=Modes,default="prod",help="Specify 'test' or 'prod' mode")
  args = parser.parse_args()
  if args.mode != Modes.PROD and args.mode != Modes.TEST:
    raise ValueError('Mode must be either "test" or "prod"')
  btc_wallet.menus.start(args)