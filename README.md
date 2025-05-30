# 問題解説

このプロジェクトは、盤面（フィールド）上に配置されたエンティティに対し、「園」と呼ばれる正方形領域を選択して 90 度回転させる操作を繰り返すことで、**指定された最大操作回数内で**、同じ数値同士のペア（隣接するマスに同じ整数がある状態）をできるだけ多く作ることを目的としています。

---

## 1. 盤面とエンティティのルール

### 1.1 盤面（フィールド）

- **形状とサイズ**
  - 盤面は正方形で、サイズは `S x S` となります。
  - 利用可能なサイズ `S` は、最小 4、最大 24 の**偶数**です。（例：4x4, 6x6, ..., 24x24）
  - **プロトタイプ段階では、サイズを 16x16 に固定して開発します。**

### 1.2 エンティティ

- **定義と値の範囲**
  - 各マスには整数値が割り当てられ、これを「エンティティ」と呼びます。
  - 値の範囲は 0 から `(S*S / 2) - 1` までとなります。
  - 盤面全体で、各整数値は必ずちょうど 2 個ずつ存在します。
    - 例：4x4 の盤面 (S=4) の場合、マス数は 16。エンティティの値は 0 から (16/2)-1 = 7 まで。0 から 7 の各整数が 2 個ずつ存在します。

### 1.3 座標系

- **説明**
  - 各セルの位置は `(x, y)` の座標で表され、左上のセルが `(0, 0)` となります。
  - `x` が列（横方向）、`y` が行（縦方向）を表します。

### 1.4 ペアの定義

- **隣接条件**
  - 同じ整数値のエンティティが、上下左右（4 近傍）のいずれかに隣接している状態を「ペア」と呼びます。
  - ペアの形としては、縦型 (`(x, y)` と `(x, y+1)`) または横型 (`(x, y)` と `(x+1, y)`) の 2 種類があります。
  - 斜めはペアとはみなしません。

## 2. 操作ルール：「園」の選択と回転

プレイヤーが行える唯一の操作は、「園」と呼ばれる盤面上の正方形領域を選択し、その領域を 90 度時計回りに回転させることです。

### 2.1 園の定義

- **選択方法:** 操作は、園の左上の座標 `(x, y)` と、園の一辺の長さ `n` を指定することで定義されます。
- **サイズ `n` の制約:**
  - 最小サイズ: `n = 2`
  - 最大サイズ: `n = S - 1` （盤面サイズ `S` より 1 小さい）
  - `n` は整数であれば、偶数でも奇数でも構いません。
- **座標 `(x, y)` の制約:**
  - 園が盤面からはみ出さないように、以下の範囲で指定する必要があります。
    - `0 <= x <= S - n`
    - `0 <= y <= S - n`
- **禁止される操作:**
  - 盤面全体を選択する操作 (`n = S`) はできません。

### 2.2 回転

- **方向:** 選択された園の領域は、常に**90 度時計回り**に回転します。
- **効果:** 園の内部にあるエンティティの位置が、回転によって変化します。

## 3. ゲームの目的と終了条件

- **目的:** **指定された最大操作回数 (`max_steps`) 以内**で、最終的な盤面における**ペアの総数を最大化**することです。
- **終了条件:** 操作回数が `max_steps` に達した時点でゲーム終了となります。
  - `max_steps` は設定ファイルなどで指定されるハイパーパラメータです。

## 4. JSON フォーマット

### 4.1 問題フォーマット (`input.json`)

ゲーム開始時の盤面状態を定義します。

```json
{
  "startsAt": 1743489020, // ゲーム開始時刻のUNIX時間 (任意)
  "problem": {
    "field": {
      "size": 16, // 盤面のサイズ S (プロトタイプでは16)
      "entities": [ // S x S の二次元配列で盤面状態を表す
        [6, 3, 4, 0, ...],
        [1, 5, 3, 5, ...],
        [2, 7, 0, 6, ...],
        [1, 2, 7, 4, ...],
        // ... (S行まで続く)
      ]
    }
  }
}
```

### 4.2 操作フォーマット (`output.json`)

AlphaZero (または他のソルバー) が出力する操作のシーケンス（手順）を定義します。

```json
{
  "ops": [
    // 操作の配列 (最大 max_steps 個)
    { "x": 0, "y": 0, "n": 2 }, // 1手目: (0,0)からサイズ2の園を90度回転
    { "x": 2, "y": 2, "n": 3 } // 2手目: (2,2)からサイズ3の園を90度回転
    // ... (最大 max_steps 手まで続く)
  ]
}
```

- **`ops`**: 実行する操作 (`(x, y, n)` の指定) を順番に格納した配列です。各要素が 1 回の 90 度回転操作に対応します。
