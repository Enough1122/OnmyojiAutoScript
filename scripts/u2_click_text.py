import uiautomator2 as u2

d = u2.connect("127.0.0.1:16384")
btn = d(text="确认")
print("exists:", btn.exists(timeout=5))
if btn.exists(timeout=3):
    print("bounds:", btn.info.get("bounds"))
    btn.click()
    print("clicked by text")
else:
    print("hierarchy:", d.dump_hierarchy()[:2000])
