#src/paths.py
from pathlib import Path

#parent directory twice gets to the root
#this variable can be used anywhere to access the root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

#define variables for other common paths from the ground up
#there can also be used anywhere
DATA_DIR = ROOT_DIR / "data"

ICECUBE_DATA_DIR = DATA_DIR / "icecube_data"
ICECUBE_PASS1_DIR = DATA_DIR / "IceCube-pass1"
ICECUBE_PASS2_DIR = DATA_DIR / "IceCube-pass2"
ICECUBE_PASS3_DIR = DATA_DIR / "IceCube-pass3"


INFILL_DATA_DIR = DATA_DIR / "infill_data"
INFILL_PASS2_DIR = DATA_DIR / "Infill-pass2"

#the mock data directories are below as well, their structure resembles the real data
MOCK_DATA_DIR = ROOT_DIR / "mock_data"

MOCK_ICECUBE_DATA_DIR = MOCK_DATA_DIR / "mock_icecube_data"
MOCK_ICECUBE_PASS1_DIR = MOCK_DATA_DIR / "mock_IceCube-pass1"
MOCK_ICECUBE_PASS2_DIR = MOCK_DATA_DIR / "mock_IceCube-pass2"
MOCK_ICECUBE_PASS3_DIR = MOCK_DATA_DIR / "mock_IceCube-pass3"


MOCK_INFILL_DATA_DIR = MOCK_DATA_DIR / "mock_infill_data"
MOCK_INFILL_PASS2_DIR = MOCK_DATA_DIR / "mock_Infill-pass2"


#creates the directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

ICECUBE_DATA_DIR.mkdir(parents=True, exist_ok=True)
ICECUBE_PASS1_DIR.mkdir(parents=True, exist_ok=True)
ICECUBE_PASS2_DIR.mkdir(parents=True, exist_ok=True)
ICECUBE_PASS3_DIR.mkdir(parents=True, exist_ok=True)

INFILL_DATA_DIR.mkdir(parents=True, exist_ok=True)
INFILL_PASS2_DIR.mkdir(parents=True, exist_ok=True)


MOCK_DATA_DIR.mkdir(parents=True, exist_ok=True)

MOCK_ICECUBE_DATA_DIR.mkdir(parents=True, exist_ok=True)
MOCK_ICECUBE_PASS1_DIR.mkdir(parents=True, exist_ok=True)
MOCK_ICECUBE_PASS2_DIR.mkdir(parents=True, exist_ok=True)
MOCK_ICECUBE_PASS3_DIR.mkdir(parents=True, exist_ok=True)

MOCK_INFILL_DATA_DIR.mkdir(parents=True, exist_ok=True)
MOCK_INFILL_PASS2_DIR.mkdir(parents=True, exist_ok=True)