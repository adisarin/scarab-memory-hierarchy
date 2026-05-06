import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

benchmarks = [
    "500.perlbench_r", "502.gcc_r", "503.bwaves_r", "505.mcf_r",
    "507.cactuBSSN_r", "508.namd_r", "510.parest_r", "511.povray_r",
    "519.lbm_r", "520.omnetpp_r", "521.wrf_r", "523.xalancbmk_r",
    "525.x264_r", "526.blender_r", "527.cam4_r", "531.deepsjeng_r",
    "538.imagick_r", "541.leela_r", "544.nab_r", "548.exchange2_r",
    "549.fotonik3d_r", "554.roms_r", "557.xz_r"
]

configs = [
    "dcache_32k_4assoc", "dcache_4k_1assoc", "dcache_4k_4assoc",
    "dcache_4k_64assoc", "dcache_256k_1assoc", "dcache_256k_4assoc",
    "dcache_256k_64assoc"
]
config_labels = ["32K/4", "4K/1", "4K/4", "4K/64", "256K/1", "256K/4", "256K/64"]
simdir = os.path.expanduser("~/exp/simulations")

def parse_stat(filepath, key):
    try:
        with open(filepath) as f:
            for line in f:
                if line.strip().startswith(key + ","):
                    parts = line.strip().split(",")
                    return float(parts[-1].strip())
    except:
        pass
    return 0

# Collect 3C data: for each bench+config get compulsory, capacity, conflict counts
data = {}
for bench in benchmarks:
    data[bench] = []
    for cfg in configs:
        mem_csv = f"{simdir}/{bench}/lab2/{cfg}/memory.stat.0.csv"
        comp = parse_stat(mem_csv, "DCACHE_MISS_COMPULSORY_total_count")
        cap  = parse_stat(mem_csv, "DCACHE_MISS_CAPACITY_total_count")
        conf = parse_stat(mem_csv, "DCACHE_MISS_CONFLICT_total_count")
        total = comp + cap + conf
        if total > 0:
            data[bench].append((comp/total*100, cap/total*100, conf/total*100))
        else:
            data[bench].append((0, 0, 0))

# Add average
avg = []
for ci in range(len(configs)):
    ac = np.mean([data[b][ci][0] for b in benchmarks])
    ak = np.mean([data[b][ci][1] for b in benchmarks])
    an = np.mean([data[b][ci][2] for b in benchmarks])
    avg.append((ac, ak, an))
data["Average"] = avg
all_benchmarks = benchmarks + ["Average"]

groups = [
    all_benchmarks[0:8],
    all_benchmarks[8:16],
    all_benchmarks[16:23] + ["Average"]
]

fig, axes = plt.subplots(1, 3, figsize=(26, 5))
colors = ['#4C72B0', '#DD8452', '#55A868']  # blue=compulsory, orange=capacity, green=conflict

for gi, group in enumerate(groups):
    ax = axes[gi]
    x = np.arange(len(group))
    width = 0.11
    for ci, label in enumerate(config_labels):
        comp_vals = [data[b][ci][0] for b in group]
        cap_vals  = [data[b][ci][1] for b in group]
        conf_vals = [data[b][ci][2] for b in group]
        xpos = x + ci * width
        b1 = ax.bar(xpos, comp_vals, width, color=colors[0], label='Compulsory' if ci==0 else '')
        b2 = ax.bar(xpos, cap_vals,  width, bottom=comp_vals, color=colors[1], label='Capacity' if ci==0 else '')
        b3 = ax.bar(xpos, conf_vals, width, bottom=[c+k for c,k in zip(comp_vals,cap_vals)], color=colors[2], label='Conflict' if ci==0 else '')
        # Add config label at top
        for xp, cv, kv, nv in zip(xpos, comp_vals, cap_vals, conf_vals):
            pass
    ax.set_xticks(x + width * 3)
    ax.set_xticklabels([b.split(".")[1] if "." in b else b for b in group],
                       rotation=45, ha='right', fontsize=8)
    ax.set_ylabel("Miss Type % (stacked per config)")
    ax.set_title(f"3C Miss Classification (Part {gi+1})")
    ax.set_ylim(0, 110)
    if gi == 0:
        ax.legend(title="Miss Type", fontsize=8, title_fontsize=8)

plt.tight_layout()
plt.savefig("/home/aditya/plot_3c.png", dpi=150, bbox_inches='tight')
print("Saved plot_3c.png")
