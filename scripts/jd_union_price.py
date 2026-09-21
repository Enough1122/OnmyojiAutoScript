#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""京东联盟比价查询：关键词 -> 在售商品价格（含券/佣金），并折算单位价。

用法:
  set JD_UNION_APPKEY=xxx & set JD_UNION_SECRET=yyy   (Windows cmd)
  export JD_UNION_APPKEY=xxx JD_UNION_SECRET=yyy      (bash)
  python jd_union_price.py "洗发水 1kg" --limit 20 --sort price
  python jd_union_price.py --sku 100012043978          # 按 SKU 批量查价

状态: 骨架已写好，**未经实测** —— 需要用户注册京东联盟拿到 AppKey/AppSecret 后才能跑第一次。
      接口文档: https://jos.jd.com/apilist?apiGroupId=531 (京东联盟API)
      业务参数名以官方文档为准，首次调用若报参数错，按返回的 error 调整 goodsReq 字段。
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.jd.com/routerjson"


def _sign(params, secret):
    """宙斯签名: md5(secret + 按key排序拼接的 k+v + secret) 转大写。"""
    raw = secret + "".join(f"{k}{params[k]}" for k in sorted(params)) + secret
    return hashlib.md5(raw.encode("utf-8")).hexdigest().upper()


def call(method, biz, appkey, secret):
    p = {
        "method": method,
        "app_key": appkey,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "format": "json",
        "v": "1.0",
        "sign_method": "md5",
        "360buy_param_json": json.dumps(biz, ensure_ascii=False, separators=(",", ":")),
    }
    p["sign"] = _sign(p, secret)
    url = API + "?" + urllib.parse.urlencode(p)
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def unit_price(title, price):
    """从标题里抠出规格 -> 每 100g / 每 100ml 单价。抠不到返回 None。"""
    m = re.search(r"(\d+(?:\.\d+)?)\s*(kg|千克|公斤|g|克|ml|毫升|L|升|片|抽|包|卷)", title or "")
    if not m:
        return None
    qty, unit = float(m.group(1)), m.group(2)
    if unit in ("kg", "千克", "公斤", "L", "升"):
        base = qty * 1000
    else:
        base = qty
    if base <= 0:
        return None
    return round(float(price) / base * 100, 3), f"每100{unit if unit in ('ml','毫升','L','升') else 'g'}"


def search(keyword, limit=20, sort_name=None, appkey=None, secret=None):
    goods = {"keyword": keyword, "pageIndex": 1, "pageSize": min(limit, 30)}
    if sort_name:
        goods["sortName"] = sort_name
        goods["sort"] = "asc"
    return call("jd.union.open.goods.query", {"goodsReq": goods}, appkey, secret)


def by_sku(skus, appkey=None, secret=None):
    return call(
        "jd.union.open.goods.promotiongoodsinfo.query",
        {"skuIds": ",".join(skus)},
        appkey,
        secret,
    )


def main(argv):
    appkey = os.environ.get("JD_UNION_APPKEY")
    secret = os.environ.get("JD_UNION_SECRET")
    if not appkey or not secret:
        print("缺少 JD_UNION_APPKEY / JD_UNION_SECRET 环境变量（注册京东联盟后从应用详情里取）。")
        return 2

    if "--sku" in argv:
        data = by_sku(argv[argv.index("--sku") + 1].split(","), appkey, secret)
    else:
        kw = argv[0] if argv and not argv[0].startswith("--") else ""
        limit = 20
        if "--limit" in argv:
            limit = int(argv[argv.index("--limit") + 1])
        sort_name = argv[argv.index("--sort") + 1] if "--sort" in argv else None
        data = search(kw, limit, sort_name, appkey, secret)

    print(json.dumps(data, ensure_ascii=False, indent=2)[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
