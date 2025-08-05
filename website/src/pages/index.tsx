import React, { useState } from 'react';
import clsx from 'clsx';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import styles from './index.module.css';

function GifPopup({ open, onClose }) {
  if (!open) return null;
  return (
    <div
      style={{
        position: 'fixed',
        zIndex: 9999,
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        background: 'rgba(0,0,0,0.8)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
      onClick={onClose}
    >
      <img
        src="https://raw.githubusercontent.com/JiHungLin/llmbrick/main/examples/openai_chatbot/openai_chatbot.gif"
        alt="llmbrick demo"
        style={{
          maxWidth: '90vw',
          maxHeight: '90vh',
          borderRadius: '12px',
          boxShadow: '0 0 24px #000',
        }}
        onClick={e => e.stopPropagation()}
      />
      <button
        style={{
          position: 'absolute',
          top: 32,
          right: 48,
          fontSize: 32,
          color: '#fff',
          background: 'transparent',
          border: 'none',
          cursor: 'pointer',
        }}
        onClick={onClose}
        aria-label="關閉"
      >
        ×
      </button>
    </div>
  );
}

function HomepageHeader() {
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          llmbrick
        </Heading>
        <p className="hero__subtitle">
          一個強調「模組化設計」、「明確協定定義」、「靈活組裝」與「易於擴展」的 LLM 應用開發框架。
        </p>
        <div>
          <a
            href="https://pypi.org/project/llmbrick/"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'inline-block',
              marginTop: '1.5rem',
            }}
          >
            <img
              src="https://img.shields.io/pypi/v/llmbrick?label=PyPI%20llmbrick&style=for-the-badge"
              alt="PyPI Version"
              style={{
                height: '44px',
                minWidth: '180px',
                borderRadius: '8px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.10)',
                background: '#fff',
                padding: '0 8px',
                objectFit: 'contain',
              }}
            />
          </a>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  const [popupOpen, setPopupOpen] = useState(false);

  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />"
    >
      <HomepageHeader />
      <main>
        <GifPopup open={popupOpen} onClose={() => setPopupOpen(false)} />
        <section style={{padding: '2rem 0'}}>
          <div className="container" style={{display: 'flex', flexWrap: 'wrap', alignItems: 'flex-start', gap: '2rem'}}>
            <div style={{flex: '1 1 350px', maxWidth: '400px', textAlign: 'center'}}>
              <img
                src="https://raw.githubusercontent.com/JiHungLin/llmbrick/main/examples/openai_chatbot/openai_chatbot.gif"
                alt="llmbrick demo"
                style={{maxWidth: '100%', width: '100%', borderRadius: '8px', cursor: 'pointer'}}
                onClick={() => setPopupOpen(true)}
              />
              <p style={{marginTop: '1rem'}}>OpenAI Chatbot 串流回應展示</p>
            </div>
            <div style={{flex: '2 1 500px', minWidth: '320px'}}>
              <Heading as="h2">框架特色</Heading>
              <ul>
                <li>🧱 <b>模組化設計</b>：所有功能皆以 Brick 為單元，組件可插拔、可重組，支援多層次組裝。</li>
                <li>📑 <b>明確協定定義</b>：資料流、型別、錯誤皆有明確協定，便於跨語言、跨協議整合。</li>
                <li>🔄 <b>多協議支援</b>：SSE、gRPC（WebSocket/WebRTC 計畫中），可依需求切換。</li>
                <li>🔧 <b>易於擴展</b>：插件系統與自定義組件，支援靈活擴充與客製化。</li>
                <li>⚡ <b>高效串流</b>：支援即時串流回應，適合 AI 聊天、推理、資料處理等場景。</li>
                <li>🛠️ <b>多元應用</b>：可用於 AI 聊天機器人、知識檢索、意圖判斷、資料修正、翻譯等。</li>
              </ul>
              <Heading as="h2" style={{marginTop: '2rem'}}>設計理念</Heading>
              <p>
                llmbrick 強調「協定導向」與「靈活組裝」，每個 Brick 可獨立開發、測試、組裝，降低耦合。PServer、Client 皆可自由組合各種 Brick，支援多種應用場景。
              </p>
              <Heading as="h2" style={{marginTop: '2rem'}}>技術架構</Heading>
              <ul>
                <li>核心模組：CommonBrick、LLMBrick、GuardBrick、IntentionBrick、RectifyBrick、ComposeBrick、RetrievalBrick、TranslateBrick</li>
                <li>協定定義：protocols/ 目錄，明確定義型別、錯誤、資料流</li>
                <li>Server 支援：SSEServer、GrpcServer，快速部署 API 與串流服務</li>
              </ul>
              <Heading as="h2" style={{marginTop: '2rem'}}>應用場景</Heading>
              <ul>
                <li>AI 聊天機器人、知識檢索、意圖判斷、資料修正、翻譯、API 串流服務</li>
              </ul>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
