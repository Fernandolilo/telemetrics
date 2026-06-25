from bleak import BleakScanner, BleakClient
import asyncio


class BluetoothService:

    def __init__(self):
        self.client = None
        self.uart_char = "0000fff1-0000-1000-8000-00805f9b34fb"
        self.rx_buffer = ""
        self.lock = asyncio.Lock()

    async def find_and_connect_by_name(self, keywords, timeout=10):

        devices = await BleakScanner.discover(timeout=timeout)

        for d in devices:
            name = d.name or "UNKNOWN"
            print(f"{name} | {d.address}")

            if any(k.lower() in name.lower() for k in keywords):

                print(f"\nSelecionado: {name}")

                self.client = BleakClient(d.address)
                await self.client.connect()

                if not self.client.is_connected:
                    return False

                await self.client.start_notify(
                    self.uart_char,
                    self._notify_handler
                )

                return True

        return False

    # 🔥 recebe dados contínuos
    def _notify_handler(self, sender, data):
        text = data.decode(errors="ignore")
        self.rx_buffer += text

    async def send(self, cmd: str, delay=0.3):

        async with self.lock:

            self.rx_buffer = ""  # 🔥 limpa antes de cada comando

            await self.client.write_gatt_char(
                self.uart_char,
                (cmd + "\r").encode()
            )

            await asyncio.sleep(delay)

            resp = self.rx_buffer
            self.rx_buffer = ""

            return self._clean(resp)

    def _clean(self, data: str):
        if not data:
            return None

        return (
            data.replace(" ", "")
                .replace("\r", "")
                .replace("\n", "")
                .replace(">", "")
        )