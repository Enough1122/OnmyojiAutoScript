import sys
import uiautomator2 as u2

x, y = int(sys.argv[1]), int(sys.argv[2])
d = u2.connect("127.0.0.1:16384")
print("connected:", d.info.get("displaySize"))
d.click(x, y)
print(f"clicked {x},{y}")
