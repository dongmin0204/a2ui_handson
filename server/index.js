const express = require("express");
const { GoogleAuth } = require("google-auth-library");
const fs = require("fs");
const path = require("path");
const { SYSTEM_PROMPT, ACTION_PROMPT, MODEL_ID, LOCATION } = require("./systemPrompt.js");

// .env 파일 직접 파싱
const envPath = path.resolve(__dirname, "../.env");
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, "utf-8");
  for (const line of envContent.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eqIdx = trimmed.indexOf("=");
    if (eqIdx === -1) continue;
    const key = trimmed.slice(0, eqIdx).trim();
    const val = trimmed.slice(eqIdx + 1).trim();
    if (key && !process.env[key]) {
      process.env[key] = val;
    }
  }
}

const app = express();
app.use(express.json({ limit: "10mb" }));

const PROJECT_ID = process.env.GCP_PROJECT_ID;
const PORT = process.env.PORT || 3001;

const auth = new GoogleAuth({
  scopes: ["https://www.googleapis.com/auth/cloud-platform"],
});

async function callGemini(userMessage, systemInstruction = SYSTEM_PROMPT) {
  if (!PROJECT_ID) {
    throw new Error(
      "GCP_PROJECT_ID가 설정되지 않았습니다. .env 파일을 확인하세요."
    );
  }

  const ENDPOINT = `https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/${MODEL_ID}:generateContent`;

  const client = await auth.getClient();
  const accessToken = await client.getAccessToken();

  const requestBody = {
    contents: [{ role: "user", parts: [{ text: userMessage }] }],
    systemInstruction: { parts: [{ text: systemInstruction }] },
    generationConfig: {
      temperature: 0.7,
      maxOutputTokens: 8192,
      responseMimeType: "application/json",
    },
  };

  const response = await fetch(ENDPOINT, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken.token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Vertex AI ${response.status}: ${err}`);
  }

  const data = await response.json();
  const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error("Gemini 응답이 비어있습니다.");

  const cleaned = text.replace(/```json\n?|```\n?/g, "").trim();
  return JSON.parse(cleaned);
}

app.post("/api/generate", async (req, res) => {
  try {
    const { prompt } = req.body;
    if (!prompt) {
      return res.status(400).json({ error: "프롬프트를 입력하세요." });
    }
    const result = await callGemini(prompt);
    res.json(result);
  } catch (err) {
    console.error("Generate error:", err.message);
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/action", async (req, res) => {
  try {
    const { action, context, currentDataModel, surfaceId } = req.body;
    const prompt = ACTION_PROMPT(action, context, currentDataModel, surfaceId);
    const result = await callGemini(prompt);
    res.json(result);
  } catch (err) {
    console.error("Action error:", err.message);
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`\n A2UI Server: http://localhost:${PORT}`);
  console.log(` Project: ${PROJECT_ID || "(미설정 — .env에 GCP_PROJECT_ID 입력 필요)"}`);
  console.log(` Model: ${MODEL_ID}`);
  console.log(` Location: ${LOCATION}\n`);
});
