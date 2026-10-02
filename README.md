# SEO Update — GitHub Pages

Halaman utama sengaja bernama `seo-update.html`, bukan `index.html`.

## Yang diperbaiki pada v2
- Workflow berjalan otomatis setelah perubahan workflow/script di branch `main`.
- Tetap bisa dijalankan manual melalui **Actions → Update SEO Feed → Run workflow**.
- RSS dicek setiap 30 menit.
- Jika semua RSS gagal, workflow **gagal dan tidak menimpa data lama dengan data kosong**.
- Parser RSS/Atom diperbaiki untuk namespace XML.
- `data.json` menjadi sumber data halaman.

## Setup
1. Upload semua file/folder ke repository GitHub pada branch `main`.
2. Pastikan **Actions** di repository tidak dinonaktifkan.
3. Buka **Actions → Update SEO Feed**.
4. Klik **Run workflow** untuk pertama kali.
5. Tunggu workflow selesai dengan tanda hijau.
6. Pastikan `data.json` berubah dan berisi artikel.
7. Buka GitHub Pages:
   `https://USERNAME.github.io/REPOSITORY/seo-update.html`

## Jika masih 0 artikel
Jangan ubah HTML. Cek:
- Actions → Update SEO Feed → job terakhir
- Apakah statusnya hijau?
- Apakah `data.json` berisi `items`?
- Jika job merah, buka log job untuk melihat sumber RSS yang gagal.
