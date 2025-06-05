# *d–q* 電流モデルの前進オイラー離散化  
— 数値解析的背景と代表的英語文献（日本語抄訳付き）—

---

## 概要

連続時間の PMSM (*Permanent-Magnet Synchronous Motor*) 電流方程式  

$
\dot i_d = \frac{V_d - R i_d}{L_d}, \qquad
\dot i_q = \frac{V_q - R i_q}{L_q}
$

をサンプリング間隔 \(T_s\) で **前進オイラー法** (explicit Euler) により積分すると

$
\begin{aligned}
i_d[k\!+\!1] &= i_d[k] + \tfrac{T_s}{L_d}\bigl(V_d[k]-R\,i_d[k]\bigr)\\
i_q[k\!+\!1] &= i_q[k] + \tfrac{T_s}{L_q}\bigl(V_q[k]-R\,i_q[k]\bigr)
\end{aligned}
$

という一次帰帰式になります。実装が極めて容易な反面、電機子時定数 \(L/R\) より大きいステップ長では数値的不安定が起こりやすいため、実機ドライブでは **後退（Backward）オイラー** や **トラペゾイダル（Tustin）** 法へ切り替える例も多いです。

---

## 1. 連続-時間 *d–q* モデルと離散化の位置づけ

| 資料 | 概要 | リンク |
|---|---|---|
| MathWorks **PMSM (DQ0)** ブロック | 連続式と離散化の双方を示し、固定サンプル時間シミュレーションでは explicit Euler を利用することを解説。 | <https://de.mathworks.com/help/sps/ref/pmsmdq0.html> |
| TI C2000™ FAQ | 組込み FOC 例として同式を提示し「PI 電流ループの内部モデルは *vdq* を『スケール値』として扱う」点を注意。 | <https://e2e.ti.com/support/microcontrollers/c2000-microcontrollers-group/c2000/f/c2000-microcontrollers-forum/622017/pmsm-dq-model-equation> |
| IEEE PELS 講義資料 “Derivation and Real-World Use of DQ Transform for Motor Drives” | dq 変換→モータモデル→電流制御の流れを図と波形で解説し、離散化例を掲載。 | <https://r6.ieee.org/scv-pels/wp-content/uploads/sites/108/feb2018_dq_transform_ogorman-1.pdf> |

### 日本語抄訳（要点）

1. **d–q 軸電流方程式**

   $
   \dot i_d=\frac{1}{L_d}\!\bigl(V_d - R i_d + \omega_e L_q i_q\bigr),\quad
   \dot i_q=\frac{1}{L_q}\!\bigl(V_q - R i_q - \omega_e L_d i_d - \omega_e \psi_f\bigr)
   $

2. **数値離散化の比較**

| 方法 | 特徴 | 安定条件／適用の目安 |
|------|------|------------------|
| **前進オイラー** | 明示的・一次精度・実装容易 | \(T_s < 2L/R\) で安定 |
| **後退オイラー** | 暗黙形・一次精度・A/L-安定 | 時定数が短い電流ループでも安定 |
| **トラペゾイダル (Tustin)** | 二次精度・位相遅れ小 | 高忠実度シミュレーションやサーボドライブ |

---

## 2. オイラー法の数値解析的背景

| 方式 | 特徴 | モータ応用例 |
|------|------|-------------|
| 前進オイラー | 明示的・計算軽いが剛性に弱い | DSP/マイコン学習用簡易モデル |
| 後退オイラー | 暗黙形・A/L-安定 | Simulink® **PMSM Current Controller** 等 |
| トラペゾイダル | 二次精度・位相遅れ最小 | Simscape Electrical™ 高忠実度モデル |

### 参考資料

* ScienceDirect Topics — *Backward Euler*（安定領域図と剛性 ODE 解説）  
  <https://www.sciencedirect.com/topics/engineering/backward-euler>
* LibreTexts “Backward Euler Method”（導出と誤差解析）  
  <https://math.libretexts.org/.../1.03:_Backward_Euler_method>
* Wikipedia *Backward Euler method*（A-安定性の詳細）  
  <https://en.wikipedia.org/wiki/Backward_Euler_method>

---

## 3. 代表的英語文献と日本語概略

| 区分 | 原典 | 日本語でのポイント |
|---|---|---|
| **教科書** | “Models of Electric Machines” – Univ. of Utah | dq 変換を厳密導出し、前進／後退オイラー離散化を演習課題に。 |
| **学術論文** | MDPI *Machines* “Improved Deadbeat Current Controller of PMSM…” | 前進オイラーの不安定例を示し、Tustin による改良を検証。 |
| **学術論文** | MDPI *Sensors* “Backward EKF to Estimate and Adaptively Control a PMSM…” | EKF 離散化に後退オイラーを適用し飽和を推定。 |
| **技術レポート** | Purdue e-Pubs “Current-Controlled Brushless DC Motor Drive” | BLDC だが同形の \(i_{d,q}\) 式をオイラー離散化。 |
| **カンファレンス** | IJISET “Modeling of IPMSM Using Transient Simulation Techniques” | Forward／Backward／Trapezoidal の 3 法比較。 |
| **実装ガイド** | MathWorks “PMSM Current Controller with Pre-Control” | ディスクリート PI に後退オイラーを採用する理由を解説。 |
| **フォーラム** | TI E2E “PMSM dq model equation!” | C 実装者向けに前進オイラーのコード断片を共有。 |
| **動画教材** | YouTube “Deriving Forward & Backward Euler Integration” | 7 分で導出と安定性を可視化するチュートリアル。 |

---

## 4. 学習の進めかた

1. **数値解法の基礎**を LibreTexts や YouTube で押さえ、前進／後退の安定性差を直感的に理解する。  
2. **モータ固有の時定数** $(L/R$) を見積もり、$(T_s \ll L/R$) であれば前進オイラー、それ以外は後退オイラー／Tustin を検討。  
3. Simscape™ や C2000™ など **既成ブロックの離散化方法を確認** し、自作モデルを同一形式に合わせておくと実機との挙動差を最小化できる。

---

> 上記リンクはすべてオンラインで無償公開されています。原典 PDF を手元に置き、数式展開に日本語メモを書き加えながら読み進めると理解が深まります。
