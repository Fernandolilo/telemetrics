from bleak import BleakScanner, BleakClient
import asyncio


class BluetoothService:

    def __init__(self):
        self.client = None
        self.uart_char = "0000fff1-0000-1000-8000-00805f9b34fb"
        self.rx_buffer = ""
        self.lock = asyncio.Lock()

    async def ensure_connected(self):
        async with self.lock:

            if self.client and self.client.is_connected:
                return True

            return False


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

                self.rx_buffer = ""  # limpa buffer ao conectar
                return True

        return False


    def _notify_handler(self, sender, data):
        text = data.decode(errors="ignore")
        text = self._clean(text)

        if text:
            self.rx_buffer += text

            # limita crescimento do buffer
            if len(self.rx_buffer) > 5000:
                self.rx_buffer = self.rx_buffer[-2000:]


    def _clean(self, data: str):
        return (
            data.replace(" ", "")
                .replace("\r", "")
                .replace("\n", "")
                .replace(">", "")
        )


    async def disconnect(self):
        if self.client and self.client.is_connected:
            await self.client.disconnect()