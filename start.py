import logging
from argparse import ArgumentParser
from btc_wallet.menus import start
from btc_wallet.util import Modes

def setup_logging():
  logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                      logging.StreamHandler(),  # Console handler
                      logging.FileHandler('wallet.log')
                    ])
  console_handler = logging.getLogger().handlers[0]
  console_handler.setLevel(logging.INFO)
  console_formatter = logging.Formatter('%(message)s')
  console_handler.setFormatter(console_formatter)   

def main():
  setup_logging()
  logging.debug('Starting up')
  parser = ArgumentParser()
  parser.add_argument("--mode","-m", type=Modes, default="test", help="Specify 'test' or 'prod' mode")
  args = parser.parse_args()
  logging.debug(f"Arguments parsed: {args}")
  if args.mode not in [Modes.PROD, Modes.TEST]:
    raise ValueError('Mode must be either "test" or "prod"')
  start(args) 

if __name__ == "__main__":
    main()