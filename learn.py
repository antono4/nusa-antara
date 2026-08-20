"""Dijalankan oleh GitHub Actions setiap 30 menit untuk menambah pengetahuan."""

from nusa_antara.learner import learn_once

if __name__ == "__main__":
    print(learn_once())
