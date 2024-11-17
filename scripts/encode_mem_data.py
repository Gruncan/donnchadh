import json
from datetime import datetime

mem_key_table = {"nr_free_pages": "0x0", "nr_zone_inactive_anon": "0x1","nr_zone_active_anon": "0x2","nr_zone_inactive_file": "0x3","nr_zone_active_file": "0x4","nr_zone_unevictable": "0x5","nr_zone_write_pending": "0x6","nr_mlock": "0x7","nr_bounce": "0x8","nr_zspages": "0x9","nr_free_cma": "0xa","nr_unaccepted": "0xb","numa_hit": "0xc","numa_miss": "0xd","numa_foreign": "0xe","numa_interleave": "0xf","numa_local": "0x10","numa_other": "0x11","nr_inactive_anon": "0x12","nr_active_anon": "0x13","nr_inactive_file": "0x14","nr_active_file": "0x15","nr_unevictable": "0x16","nr_slab_reclaimable": "0x17","nr_slab_unreclaimable": "0x18","nr_isolated_anon": "0x19","nr_isolated_file": "0x1a","workingset_nodes": "0x1b","workingset_refault_anon": "0x1c","workingset_refault_file": "0x1d","workingset_activate_anon": "0x1e","workingset_activate_file": "0x1f","workingset_restore_anon": "0x20","workingset_restore_file": "0x21","workingset_nodereclaim": "0x22","nr_anon_pages": "0x23","nr_mapped": "0x24","nr_file_pages": "0x25","nr_dirty": "0x26","nr_writeback": "0x27","nr_writeback_temp": "0x28","nr_shmem": "0x29","nr_shmem_hugepages": "0x2a","nr_shmem_pmdmapped": "0x2b","nr_file_hugepages": "0x2c","nr_file_pmdmapped": "0x2d","nr_anon_transparent_hugepages": "0x2e","nr_dirty_threshold": "0x2f","nr_dirty_background_threshold": "0x30","pgpgin": "0x31","pgpgout": "0x32","pswpin": "0x33","pswpout": "0x34","pgfault": "0x35","pgmajfault": "0x36","pgalloc_dma": "0x37","pgalloc_dma32": "0x38","pgalloc_normal": "0x39","pgalloc_movable": "0x3a","pgalloc_device": "0x3b","allocstall_dma": "0x3c","allocstall_dma32": "0x3d","allocstall_normal": "0x3e","allocstall_movable": "0x3f","allocstall_device": "0x40","pgskip_dma": "0x41","pgskip_dma32": "0x42","pgskip_normal": "0x43","pgskip_movable": "0x44","pgskip_device": "0x45","pgfree": "0x46","pgactivate": "0x47","pgdeactivate": "0x48","pglazyfree": "0x49","pglazyfreed": "0x4a","pgrefill": "0x4b","pgreuse": "0x4c","pgsteal_kswapd": "0x4d","pgsteal_direct": "0x4e","pgsteal_khugepaged": "0x4f","pgscan_kswapd": "0x50","pgscan_direct": "0x51","pgscan_khugepaged": "0x52","pgscan_direct_throttle": "0x53","pgscan_anon": "0x54","pgscan_file": "0x55","pgsteal_anon": "0x56","pgsteal_file": "0x57","zone_reclaim_failed": "0x58","pginodesteal": "0x59","slabs_scanned": "0x5a","kswapd_inodesteal": "0x5b","kswapd_low_wmark_hit_quickly": "0x5c","kswapd_high_wmark_hit_quickly": "0x5d","pageoutrun": "0x5e","pgrotated": "0x5f","drop_pagecache": "0x60","drop_slab": "0x61","oom_kill": "0x62","numa_pte_updates": "0x63","numa_huge_pte_updates": "0x64","numa_hint_faults": "0x65","numa_hint_faults_local": "0x66","numa_pages_migrated": "0x67","pgmigrate_success": "0x68","pgmigrate_fail": "0x69","thp_migration_success": "0x6a","thp_migration_fail": "0x6b","thp_migration_split": "0x6c","compact_migrate_scanned": "0x6d","compact_free_scanned": "0x6e","compact_isolated": "0x6f","compact_stall": "0x70","compact_fail": "0x71","compact_success": "0x72","compact_daemon_wake": "0x73","compact_daemon_migrate_scanned": "0x74","compact_daemon_free_scanned": "0x75","htlb_buddy_alloc_success": "0x76","htlb_buddy_alloc_fail": "0x77","unevictable_pgs_culled": "0x78","unevictable_pgs_scanned": "0x79","unevictable_pgs_rescued": "0x7a","unevictable_pgs_mlocked": "0x7b","unevictable_pgs_munlocked": "0x7c","unevictable_pgs_cleared": "0x7d","unevictable_pgs_stranded": "0x7e","thp_fault_alloc": "0x7f","thp_fault_fallback": "0x80","thp_fault_fallback_charge": "0x81","thp_collapse_alloc": "0x82","thp_collapse_alloc_failed": "0x83","thp_file_alloc": "0x84","thp_file_fallback": "0x85","thp_file_fallback_charge": "0x86","thp_file_mapped": "0x87","thp_split_page": "0x88","thp_split_page_failed": "0x89","thp_deferred_split_page": "0x8a","thp_split_pmd": "0x8b","thp_scan_exceed_none_pte": "0x8c","thp_scan_exceed_swap_pte": "0x8d","thp_scan_exceed_share_pte": "0x8e","thp_split_pud": "0x8f","thp_zero_page_alloc": "0x90","thp_zero_page_alloc_failed": "0x91","thp_swpout": "0x92","thp_swpout_fallback": "0x93","balloon_inflate": "0x94","balloon_deflate": "0x95","balloon_migrate": "0x96","swap_ra": "0x97","swap_ra_hit": "0x98","ksm_swpin_copy": "0x99","cow_ksm": "0x9a","zswpin": "0x9b","zswpout": "0x9c","zswpwb": "0x9d","direct_map_level2_splits": "0x9e","direct_map_level3_splits": "0x9f","nr_unstable": "0xa0","total": "0xa1","free": "0xa2","available": "0xa3","buffers": "0xa4","cached": "0xa5","swapCache": "0xa6","active": "0xa7","inActive": "0xa8","activeAnon": "0xa9","inActiveAnon": "0xaa","activeFile": "0xab","inActiveFile": "0xac","unevictable": "0xad","mLocked": "0xae","swapTotal": "0xaf","swapFree": "0xb0","zswap": "0xb1","zswapped": "0xb2","dirty": "0xb3","writeback": "0xb4","pagesAnon": "0xb5","pageMapped": "0xb6","shmem": "0xb7","kreClaimable": "0xb8","slab": "0xb9","srClaimable": "0xba","sunReclaim": "0xbb","kernelStack": "0xbc","pageTables": "0xbd","secPageTables": "0xbe","nfsUnstable": "0xbf","bounce": "0xc0","writebackTmp": "0xc1","commitLimit": "0xc2","committedAllocs": "0xc3","vmallocTotal": "0xc4","vmallocUsed": "0xc5","vmallocChunk": "0xc6","perCPU": "0xc7","hardwareCorrupted": "0xc8","hugePagesAnon": "0xc9","hugePagesShmem": "0xca","pmdMappedShmem": "0xcb","hugePagesFile": "0xcc","pmdMappedFile": "0xcd","unaccepted": "0xce","hugePagesTotal": "0xcf","hugePagesFree": "0xd0","hugePagesRsvd": "0xd1","hugePagesSurp": "0xd2","hugePageSize": "0xd3","hugePageTLB": "0xd4","directMap4k": "0xd5","directMap2M": "0xd6","directMap1G": "0xd7"
                 , "oomAdj": "0xd8", "oomScore": "0xd9", "oomScoreAdj": "0xda", "p_size": "0xdb", "p_resident": "0xdc", "p_shared": "0xdd", "p_text": "0xde", "p_data": "0xdf", "p_dirty": "0xe0"}

date_format = "%Y-%m-%d %H:%M:%S.%f"

VERSION = 1

def encode_datetime(dt):
    obj = datetime.strptime(dt, date_format)
    year_bits = int(str(obj.year)[2:])
    month_bits = obj.month - 1
    day_bits = obj.day - 1
    hour_bits = obj.hour
    minute_bits = obj.minute - 1
    second_bits = obj.second - 1

    offsets = [7, 4, 5, 4, 6, 6]
    datetime_bits = [year_bits, month_bits, day_bits, hour_bits, minute_bits, second_bits]

    summation = 0b0
    offset = sum(offsets)
    for bits, os in zip(datetime_bits, offsets):
        offset -= os
        v = min(bits, (2 ** os)) << offset
        summation |= v

    return hex(summation)[2:]

def encode_milliseconds(current_dt, prev_dt):
    obj = datetime.strptime(current_dt, date_format)
    prev_dt_obj = datetime.strptime(prev_dt, date_format)

    milliseconds = (obj.microsecond - prev_dt_obj.microsecond) # This is actually milliseconds offset

    return hex(milliseconds & 24)[2:]

def encode_version(vers):
    return hex(vers)[2:]

def encode_mem_data(mem_data):
    sb = ""

    for key, value in mem_data.items():
        sb += mem_key_table[key][2:]
        value = max(int(value), 0)
        value = min(value, (2 ** 16)-1)
        hex_value = hex(value)[2:]
        l = hex(len(str(value)))[2:]
        sb += l + hex_value

    return sb

def encode_mem_file(mem_file):
    lines = []
    with open(mem_file, "r") as f:
        for line in f.readlines():
            try:
                lines.append(json.loads(line))
            except:  # Potentially write failed..
                continue

    sb = ""
    sb += encode_version(VERSION)

    prev_date = list(lines[0].keys())[0]

    sb += encode_datetime(prev_date)

    for line in lines:
        date = list(line.keys())[0]
        sb += encode_milliseconds(date, prev_date)

        values = line[date]
        v = encode_mem_data(values)

        sb += v


    return sb



def print_binary_output(encoded_data):
    byte_data = encoded_data.encode('utf-8')

    binary_output = "".join(f"{byte:08b}" for byte in byte_data)
    print(f"Length: {len(binary_output)/8}")
    print(binary_output)


encoded = encode_mem_file("allocation_free.json")

length = len(encoded)

if length % 2 != 0:
    encoded = encoded.zfill(length + 1)


with open("allocation_free_encode.mtc", "wb") as f:
    f.write(bytes.fromhex(encoded))

