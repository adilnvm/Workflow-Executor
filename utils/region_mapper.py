CITY_TO_REGION = {
    # WEST INDIA
    "mumbai": "west_india", "pune": "west_india", "ahmedabad": "west_india", "surat": "west_india",
    "vadodara": "west_india", "rajkot": "west_india", "nashik": "west_india", "nagpur": "west_india",
    "aurangabad": "west_india", "thane": "west_india", "navi mumbai": "west_india", "solapur": "west_india",
    "kolhapur": "west_india", "jamnagar": "west_india", "bhavnagar": "west_india", "panaji": "west_india",
    "vasai-virar": "west_india", "gandhinagar": "west_india",

    # NORTH INDIA
    "delhi": "north_india", "noida": "north_india", "gurgaon": "north_india", "chandigarh": "north_india",
    "jaipur": "north_india", "lucknow": "north_india", "kanpur": "north_india", "agra": "north_india",
    "varanasi": "north_india", "amritsar": "north_india", "ludhiana": "north_india", "jalandhar": "north_india",
    "shimla": "north_india", "dehradun": "north_india", "srinagar": "north_india", "jammu": "north_india",
    "ghaziabad": "north_india", "faridabad": "north_india", "meerut": "north_india", "prayagraj": "north_india",
    "bareilly": "north_india", "aligarh": "north_india", "moradabad": "north_india", "jodhpur": "north_india",
    "udaipur": "north_india", "kota": "north_india", "ajmer": "north_india", "panipat": "north_india",

    # SOUTH INDIA
    "bangalore": "south_india", "bengaluru": "south_india", "chennai": "south_india", "hyderabad": "south_india",
    "kochi": "south_india", "coimbatore": "south_india", "madurai": "south_india", "mysore": "south_india",
    "visakhapatnam": "south_india", "vijayawada": "south_india", "thiruvananthapuram": "south_india",
    "trivandrum": "south_india", "salem": "south_india", "tiruchirappalli": "south_india", "warangal": "south_india",
    "guntur": "south_india", "nellore": "south_india", "mangalore": "south_india", "hubli": "south_india",
    "belgaum": "south_india", "kozhikode": "south_india", "thrissur": "south_india", "pondicherry": "south_india",
    "puducherry": "south_india", "tirupati": "south_india",

    # EAST INDIA
    "kolkata": "east_india", "patna": "east_india", "bhubaneswar": "east_india", "ranchi": "east_india",
    "jamshedpur": "east_india", "dhanbad": "east_india", "cuttack": "east_india", "asansol": "east_india",
    "durgapur": "east_india", "siliguri": "east_india", "gaya": "east_india", "bhagalpur": "east_india",
    "muzaffarpur": "east_india", "puri": "east_india",

    # CENTRAL INDIA
    "indore": "central_india", "bhopal": "central_india", "jabalpur": "central_india", "gwalior": "central_india",
    "raipur": "central_india", "bilaspur": "central_india", "bhilai": "central_india", "ujjain": "central_india",
    "sagar": "central_india",

    # NORTHEAST INDIA
    "guwahati": "northeast_india", "shillong": "northeast_india", "imphal": "northeast_india",
    "agartala": "northeast_india", "kohima": "northeast_india", "aizawl": "northeast_india",
    "gangtok": "northeast_india", "itanagar": "northeast_india", "dibrugarh": "northeast_india",
    "silchar": "northeast_india"
}

def normalize_region(location: str) -> str:
    if not location:
        return "unknown"
    
    # Strip whitespace, convert to lowercase, and handle potential trailing punctuation
    key = location.strip().lower().replace(",", "")
    return CITY_TO_REGION.get(key, "unknown")