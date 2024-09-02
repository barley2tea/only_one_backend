import re
WEEK_TO_NO = {
  "MONDAY": 0, "MON": 0,
  "TUESDAY": 1, "TUE": 1,
  "WEDNESDAY": 2, "WED": 2,
  "THURSDAY": 3, "THU": 3,
  "FRIDAY": 4, "FRI": 4,
  "SATURDAY": 5, "SAT": 5,
  "SUNDAY": 6, "SUN": 6
}

def weekno(val, reverse=False):
  if reverse:
    week = [k for k, v in WEEK_TO_NO.items() if v == val and len(k) > 3]
    return week[0] if week else None
  else:
    return WEEK_TO_NO.get(val, None)
  

def getRequest(request:dict, key_list:list, default='ALL'):
  unexpected = set(key_list) - {"dormitory", "floor", "type", "id", "weekday"}
  if unexpected:
    raise ValueError("Unexpected key_list: ", unexpected)

  res = {k: request.get(k, "ALL").upper() for k in key_list}
  if "dormitory" in key_list and res["dormitory"] not in ("CEN", "MOU", "SEA", "SPA"):
    if res["dormitory"] == "ALL":
      res["dormitory"] = default
    else:
      return None

  if "floor" in key_list:
    if res["floor"] == "ALL":
      res["floor"] = default
    elif re.compile(r"[1-5]").fullmatch(res["floor"]):
      res["floor"] = int(res["floor"])
    else:
      return None

  if "type" in key_list and res["type"] not in ("WA", "DR", "PB", "SW"):
    if res["type"] == "ALL":
      res["type"] = default
    else:
      return None

  if "id" in key_list:
    if res["id"] == "ALL":
      res["id"] = default
    elif not re.compile(r'(WA|DR|SW)_[1-4]{3}|PB_(12|34|56)').fullmatch(res["id"]):
      return None

  if "weekday" in key_list:
    if res["weekday"] == "ALL":
      res["weekday"] = default
    elif re.compile(r"[0-6]").fullmatch(res["weekday"]):
      res["weekday"] = int(res["weekday"])
    else:
      week = weekno(res["weekday"])
      if week is None:
        return None
      else:
        res["weekday"] = week

  return res

