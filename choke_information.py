
class ChokeInformation:
    def __init__(self, time):
        self.uploaded_bytes = 0
        self.last_update_time = time
        self.upload_rate = 0

    def add_upload(self, time):
        time_elapsed = time - self.last_update_time
        if time_elapsed > 0:
            self.upload_rate = self.uploaded_bytes / time_elapsed
        else:
            self.upload_rate = self.upload_rate

        self.uploaded_bytes = 1
        self.last_update_time = time