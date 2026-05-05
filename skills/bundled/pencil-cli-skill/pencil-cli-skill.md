---
name: pencil-cli-integration
description: 提供使用 CLI（命令列介面）或外部腳本呼叫和與 Pencil MCP server 互動的指南與範例。當使用者想要透過外部程式自動化操作 .pen 檔案或直接呼叫 Pencil 工具時觸發此技能。
---

# Pencil CLI 整合指南

## 概述
Pencil 是一個基於 Context Protocol (MCP) 架構的伺服器。這表示您可以透過任何符合 MCP 標準的客戶端（Client），經由標準輸入/輸出 (`stdio`) 向它發送 JSON-RPC 請求來進行互動。這份指南將教你如何使用命令列與指令碼呼叫 Pencil 的功能，例如 `batch_design`、`get_editor_state` 等。

## 途徑 1：使用官方 MCP Inspector (最適合測試與開發)
如果您只是想要在終端機啟動並快速測試 Pencil 的工具，可以使用官方提供的 `@modelcontextprotocol/inspector`：

```bash
# 替換為實際啟動 Pencil 伺服器的執行檔或指令
npx @modelcontextprotocol/inspector <pencil_server_executable>
```
這會在本地端開啟一個除錯面板，讓你可以直接在網頁介面上選擇工具並送出 JSON 參數結構給 Pencil，完全不用自己寫底層的通訊協定。

---

## 途徑 2：使用 Node.js 撰寫自訂 CLI 客戶端
若是想要寫成自己專屬的 CLI 小工具（例如每天自動產出 .pen 設計圖、或是批次修改 .pen 檔案），可以直接透過 TypeScript/JavaScript 呼叫。

### 步驟 1: 安裝依賴
```bash
npm install @modelcontextprotocol/sdk
```

### 步驟 2: CLI 呼叫範例程式 (`pencil-cli.js`)
以下是一個透過 `stdio` 連接 Pencil MCP Server 並呼叫 `mcp_pencil_get_editor_state` 工具的簡單範例：

```javascript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function run() {
  // 1. 設定 Transport (需設定為您實際 Pencil Server 的執行路徑)
  const transport = new StdioClientTransport({
    command: "path/to/pencil/server/executable", // <--- 替換為您的 Pencil Server 路徑
    args: [] 
  });

  const client = new Client(
    { name: "my-pencil-cli", version: "1.0.0" },
    { capabilities: { tools: {} } }
  );

  // 2. 連接伺服器
  await client.connect(transport);
  console.log("成功連接到 Pencil MCP Server!");

  // 3. 呼叫工具 (以取得編輯器狀態為例)
  try {
    const result = await client.callTool({
      name: "mcp_pencil_get_editor_state",
      arguments: {
        include_schema: false
      }
    });
    
    console.log("Pencil 回傳結果：");
    console.dir(result, { depth: null });
    
  } catch (error) {
    console.error("呼叫失敗:", error);
  } finally {
    // 4. 斷開連線
    process.exit(0);
  }
}

run();
```

### 常見使用場景參數提示
如果您要寫腳本呼叫最具威力的 `mcp_pencil_batch_design`，其 `arguments` 結構如下：
```javascript
const result = await client.callTool({
  name: "mcp_pencil_batch_design",
  arguments: {
    filePath: "path/to/your/design.pen",
    operations: "screen=I(document, {type: 'frame', name: 'CLI Generated Screen', width: 800, height: 600, placeholder: true})"
  }
});
```

## 注意事項與限制
1. **加密限制**：`.pen` 檔案的內容是被加密且私有的，**絕對不能**嘗試用一般的文件讀取方式（如 `cat`、`fs.readFileSync`）去解析它，必須且只能透過 Pencil MCP Server 提供的工具（如 `mcp_pencil_batch_get`、`mcp_pencil_batch_design`）來進行讀寫與解析。
2. **連線模式**：預設情況下，CLI 工具使用 `stdio` 傳輸（標準輸入/輸出）。請確保在啟動 Server 時，不要在 stdout 印出除了 MCP JSON-RPC 以外的雜訊字串（例如 `console.log`），這會導致協議解析失敗。
3. **路徑使用**：當傳遞 `filePath` 時，盡量使用**絕對路徑**，確保伺服器能夠正確找到 `.pen` 檔案位置。
