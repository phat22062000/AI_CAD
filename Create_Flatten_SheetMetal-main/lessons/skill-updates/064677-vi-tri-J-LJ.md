# Cập nhật skill dxf-sheetmetal: vị trí J/LJ (đơn 521030-09, 064677, người dùng chốt 30/10/2026)

Sửa mục 10 (dòng 146 và 147 của SKILL.md hiện tại, thay nguyên 2 dòng):

Dòng 146 (cũ): `  - J đầu ở x = 30, LJ ở x = L - 30 (ngoài cùng phải); N = số J + 1 điểm chia đều, bước (L - 60)/(N - 1). ...`

Dòng 146 (mới):
  - J đầu cách đầu mép thẳng trên 30, LJ cách cuối mép thẳng trên 30: x_đầu, x_cuối là hai đầu của đoạn thẳng mép trên, bỏ đoạn vát C ở đầu (góc bo R không trừ); mép trên không vát thì x_đầu = 0, x_cuối = L. N = số J + 1 điểm chia đều, bước (x_cuối - x_đầu - 60)/(N - 1). Ví dụ 2J + LJ: x_đầu + 30, giữa, x_cuối - 30.

Dòng 147 (cũ): `  - Ví dụ 26-057101 (1199.5 x 99.5): POINT (30; 99.5) + TEXT J, POINT (1169.5; 99.5) + TEXT LJ.`

Dòng 147 (mới), giữ ví dụ cũ và thêm:
  - Ví dụ 26-057101 (1199.5 x 99.5): POINT (30; 99.5) + TEXT J, POINT (1169.5; 99.5) + TEXT LJ. Ví dụ 26-064677 (COVER A+B 1110 x 98.544, mép trên vát C20 hai đầu, đoạn thẳng 20 → 1090, xoay 180° để mép thẳng có C20 nằm trên, tai uốn ở dưới): POINT (50; 98.544) + TEXT J, POINT (1060; 98.544) + TEXT LJ.

Kèm: dxf_check.py (mục J/LJ) đã sửa theo cùng quy tắc, bản trong /mnt/project-files/tools/ (43803 byte); bản sao AI_Work\tools chưa commit được (bị chặn quyền ghi đè).
