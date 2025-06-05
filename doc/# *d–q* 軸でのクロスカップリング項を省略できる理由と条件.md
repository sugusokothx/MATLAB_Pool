# *d–q* 軸でのクロスカップリング項を省略できる理由と条件

以下では *d–q* 軸電流式から電気角速度 \$\omega\$ に比例する「クロスカップリング項」（\$\omega L\_d i\_q\$，\$\omega L\_q i\_d\$，\$\omega\psi\_f\$ など）を省略できる代表的な理由を整理し，その背後にある条件を文献に基づいて説明します。**要点を一文でまとめると，低速／停止や高周波注入など「機械的回転が支配的でない局面」では \$\omega\simeq0\$ あるいは制御器のフィードフォワード補償で済むため，実務では RL 要素のみを残す簡易モデルが頻繁に使われます。**

---

## 1  クロスカップリング項とは

連続時間の標準 *dq* 方程式は

$$
\begin{aligned}
\dot i_d &= \frac{1}{L_d}\!\bigl(V_d - R i_d + \omega L_q i_q \bigr),\\
\dot i_q &= \frac{1}{L_q}\!\bigl(V_q - R i_q - \omega L_d i_d - \omega\psi_f\bigr)
\end{aligned}
$$

で，右辺の \$\omega\$ に比例する 3 つが「クロスカップリング（速度依存）項」に当たります \[1]．

---

## 2  省略が許される 4 つの典型ケース

| ケース                  | 省略できる根拠                                              | 代表文献                      |
| :------------------- | :--------------------------------------------------- | :------------------------ |
| **a) 停止・極低速**        | センサレス起動用 HF 注入や組立検査では \$\omega\approx0\$ → カップリング項＝0 | Trace \[2], Infineon \[3] |
| **b) 低速域 FOC**       | 実機速度（数百 rpm 程度以下）では誘導電圧が小さく RL ダイナミクスが支配的            | ResearchGate Q\&A \[4]    |
| **c) フィードフォワード補償**   | 制御器側で \$+\omega\$ 項を前向きに加算して電流ループを**デカップリング**する実装が多い | TI E2E \[5]               |
| **d) 学習／簡易シミュレーション** | Euler 離散化やゲイン調整を説明する教材では最小限の一次 RL を示し数値安定性のみ議論       | Microchip 教材 \[6]         |

### 補足

* 速度が上がるとクロスカップリング無視はトルクリップル増大や不安定の原因となるため，高速域や磁束弱め制御では**必ず補償が必要**です \[7]\[8]。
* 速度ゼロでも **相互インダクタンス飽和** が強い IPMSM では誤差源になり得るとの指摘もあります \[9]\[10]。

---

## 3  省略式の数値離散化と適用範囲

クロスカップリングを除いた \$RL\$ のみの式を前進オイラーで離散化すると

$$
i_d[k+1]=i_d[k]+\frac{T_s}{L_d}\bigl(V_d-R\,i_d[k]\bigr)
$$

となります。シミュレーション上，

* **時定数 \$\tau=L/R \gg T\_s\$**
* **検討対象が電流制御内輪のゲイン・応答時間のみ**

であれば十分な近似とみなせます。しかし **高速域や精密トルク解析** には不適切で，速度依存項を後から追加するか，後退オイラー／Tustin で厳密に離散化した式を使うことが推奨されます \[11]\[12]。

---

## 4  情報が見つからなかった場合の扱い

本回答では公開資料 10 件を調査し，クロスカップリング項省略に言及する十分な情報を確認できました。したがって「見つからない」という状況は該当しません。

---

### 参考オンライン資料

1. IET Journal 論文 *Cross-Coupling Magnetic Saturation in PMSM* \[1]
2. UT Knoxville 修士論文 *High-Frequency Injection Sensorless Control for a PMSM* \[2]
3. Infineon App-Note *Position Estimation of PMSM with Signal Injection* \[3]
4. ResearchGate Q\&A “Why the currents on d-q axis can be controlled independently …” \[4]
5. TI E2E™ *In FOC, how does I<sub>d</sub>/I<sub>q</sub> convert to V<sub>d</sub>/V<sub>q</sub>?* \[5]
6. Microchip App-Note *Low Speed Open-Loop FOC for PMSM* \[6]
7. MDPI *Sensors* 論文 *Cross-Coupling Factors Estimation for IPMSM* \[7]
8. TI E2E™ スレッド *FOC Control of PMSM motors (finding Vd and Vq)* \[8]
9. Nature Scientific Reports *Sensorless control in full-speed domain of IPMSM* \[9]
10. SpringerLink 論文 *Comprehensive analysis of IPMSM drives with FOC …* \[10]
11. Microchip App-Note *AN1160 Sensorless BLDC Control* \[11]
12. TI 技術ドキュメント *High-Voltage HEV/EV HVAC eCompressor Motor Control* \[12]
