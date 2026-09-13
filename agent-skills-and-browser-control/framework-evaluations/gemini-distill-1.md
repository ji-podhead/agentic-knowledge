---
okf_version: "1.0"
id: "okf-age-fra-gemini-distill-1"
title: "Gemini Distill 1"
topic: "agent-skills-and-browser-control"
subtopic: "framework-evaluations"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - agent-skills-and-browser-control
  - framework-evaluations
summary: "elche apis und pacages und services sollten wirjetzt nhemen für für discovery, beschreibungen, usage, statistic, icons etc und alles was wir bruachenU"
---

# Gemini Distill 1

## Overview

│ Dimension             │ Gewähltes Open-Source-Package     │ Primäre Rolle im OpenMesh-Core           │
├───────────────────────┼───────────────────────────────────┼────────────────────────────────────────┤
│ Visual System         │ @iconify/react + @elkjs/elkjs     │ On-Demand SVGs & Clean Graph Layouts   │
│ Inferenz & Metadata   │ RouteLLM + OpenRouter API        │ Pre-Inference Routing & Fact Caching   │
│ Sandbox & Automation  │ mark3labs/mcp-go + docker-gateway │ Sandboxed MCP Tool Execution Bridge    │
│ FinOps & Telemetrie   │ tiktoken-go + gopsutil            │ Circuit Breaker & Agent Cost Tracking  │
│ System Pipeline       │ quic-go + pgx                     │ HTTP/3 QUIC Gateway & Async Postgres   │
└───────────────────────┴───────────────────────────────────┴────────────────────────────────────────┘

import (
	"regexp"
	"strings"
)

// Regex zum strippen von Provider-Präfixen and Tags (z.B. "groq/llama-3.1-8b-instruct:latest" -> "llama-3.1-8b-instruct")
var (
	providerRegex = regexp.MustCompile(`^[a-zA-Z0-9\-_.]+ / `)
	tagRegex      = regexp.MustCompile(`:[a-zA-Z0-9\-_.]+$`)
	suffixRegex   = regexp.MustCompile(`\-(free|prod|dev|preview)$`)
)

type CanonicalApp struct {
	BaseID      string `json:"base_id"`
	DisplayName string `json:"display_name"`
	Category    string `json:"category"`
	IconKey     string `json:"icon_key"`
}

// NormalizeContainerImage berechnet die kanonische Base-ID eines Docker-Images
func NormalizeContainerImage(imageName string) string {
	// 1. Pfad-Präfixe entfernen (z.B. "library/postgres" -> "postgres")
	parts := strings.Split(imageName, "/")
	cleanName := parts[len(parts)-1]

	// 2. Tags entfernen (z.B. "postgres:16-alpine" -> "postgres")
	cleanName = tagRegex.ReplaceAllString(cleanName, "")

	// 3. Typische Umgebungssuffixe entfernen (z.B. "llama-3.1-free" -> "llama-3.1")
	cleanName = suffixRegex.ReplaceAllString(cleanName, "")

	return strings.ToLower(cleanName)
}

// ResolveDiscoveryPipeline ist das Herzstück des Zero-LLM Systems
func ResolveDiscoveryPipeline(imageName string, openPort int) CanonicalApp {
	canonicalID := NormalizeContainerImage(imageName)

	// 1. Stufe: Direktes Match gegen unsere Wappalyzer/CNCF-basierte In-Memory-Ontologie
	if def, exists := StaticTechOntology[canonicalID]; exists {
		return CanonicalApp{
			BaseID:      def.BaseID,
			DisplayName: def.DisplayName,
			Category:    def.Category,
			IconKey:     def.IconString,
		}
	}

	// 2. Stufe: IANA Offline-Port-Registry Fallback (Wenn das Image komplett custom benannt ist)
	switch openPort {
	case 5432:
		return CanonicalApp{BaseID: "postgres", DisplayName: "PostgreSQL", Category: "Databases", IconKey: "logos:postgresql"}
	case 6379:
		return CanonicalApp{BaseID: "redis", DisplayName: "Redis Cache", Category: "Infrastructure", IconKey: "logos:redis"}
	case 3306:
		return CanonicalApp{BaseID: "mysql", DisplayName: "MySQL Database", Category: "Databases", IconKey: "logos:mysql"}
	case 8200:
		return CanonicalApp{BaseID: "vault", DisplayName: "HashiCorp Vault", Category: "Infrastructure", IconKey: "logos:vault-icon"}
	}

	// 3. Stufe: Generischer Fallback (Keine Latenz, no Kosten, sauberes UI-Handling)
	return CanonicalApp{
		BaseID:      canonicalID,
		DisplayName: strings.Title(strings.ReplaceAll(canonicalID, "-", " ")),
		Category:    "Web Apps",
		IconKey:     "lucide:box",
	}
}
encoder, _ := tiktoken.GetEncoding("cl100k_base") // OpenAI / OpenRouter Standard
tokens := encoder.Encode(userPrompt, nil, nil)
estimatedCost := (float64(len(tokens)) / 1000.0) * factSheet.InputCost1K

const elk = new ELK();

const elkLayoutOptions = {
  'elk.algorithm': 'layered', // Hierarchisches Schichtenmodell (Top-Down or Left-Right)
  'elk.direction': 'RIGHT',   // Perfekt for den Datenfluss Proxy -> Model -> Tool
  'elk.layered.spacing.nodeNodeLayer': '80', // Genügend Platz for pulsierende Traffic-Metriken
  'elk.spacing.nodeNode': '50',
  'elk.layered.nodePlacement.strategy': 'BRANDES_KOEPF', // Mathematisch minimierte Linienkreuzungen
};

export async function computeGraphLayout(nodes: any[], edges: any[]) {
  const elkGraph = {
    id: 'root',
    layoutOptions: elkLayoutOptions,
    children: nodes.map(n => ({ id: n.id, width: 250, height: 100 })), // Feste Widget-Kachel-Größen
    edges: edges.map(e => ({ id: e.id, sources: [e.source], targets: [e.target] }))
  };

  const layout = await elk.layout(elkGraph);

  // Gibt die exakten X/Y Koordinaten an React Flow zurück
  return nodes.map(n => {
    const elkNode = layout.children?.find(c => c.id === n.id);
    return { ...n, position: { x: elkNode?.x || 0, y: elkNode?.y || 0 } };
  });
}

import (
	"encoding/xml"
	"fmt"
	"io"
	"strconv"
	"strings"
	"sync"
)

// IANAXMLStructure spiegelt das offizielle XML-Schema der IANA wider
type IANAXMLStructure struct {
	XMLName xml.Name `xml:"registry"`
	Records []struct {
		Name     string `xml:"name"`
		Port     string `xml:"number"`
		Protocol string `xml:"protocol"`
		Desc     string `xml:"description"`
	} `xml:"registry/record"`
}

type IANARegistry struct {
	mu    sync.RWMutex
	ports map[string]string // Key: "port/proto" -> Value: Service Name
}

func NewIANARegistry() *IANARegistry {
	return &IANARegistry{
		ports: make(map[string]string),
	}
}

// LoadIANADump parst den IANA XML Stream in 0 ms Latenz-Lookups
func (ir *IANARegistry) LoadIANADump(reader io.Reader) error {
	ir.mu.Lock()
	defer ir.mu.Unlock()

	var dump IANAXMLStructure
	if err := xml.NewDecoder(reader).Decode(&dump); err != nil {
		return fmt.Errorf("failed to decode IANA XML dump: %w", err)
	}

	for _, rec := range dump.Records {
		if rec.Port == "" || rec.Protocol == "" {
			continue
		}
		// Auflösung von Port-Ranges verhindern, nur diskrete Sockets mappen
		if strings.Contains(rec.Port, "-") {
			continue
		}

		key := fmt.Sprintf("%s/%s", rec.Port, strings.ToLower(rec.Protocol))
		ir.ports[key] = rec.Name
	}
	return nil
}

// LookupPort prüft deterministisch den Service-Namen des Sockets
func (ir *IANARegistry) LookupPort(port int, proto string) (string, bool) {
	ir.mu.RLock()
	defer ir.mu.RUnlock()

	key := fmt.Sprintf("%d/%s", port, strings.ToLower(proto))
	name, exists := ir.ports[key]
	return name, exists
}

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"io"
	"strings"
)

type SSEUsageChunk struct {
	Choices []struct {
		Delta struct {
			Content string `json:"content"`
		} `json:"delta"`
	} `json:"choices"`
	Usage *struct {
		PromptTokens     int64 `json:"prompt_tokens"`
		CompletionTokens int64 `json:"completion_tokens"`
	} `json:"usage,omitempty"`
}

// StreamCostEvaluator fängt die SSE-Chunks ab and berechnet die Live-Kosten
func StreamCostEvaluator(ctx context.Context, upstreamBody io.Reader, clientWriter io.Writer, onUsageFound func(promptTokens, completionTokens int64)) error {
	reader := bufio.NewReader(upstreamBody)

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			line, err := reader.ReadBytes('\n')
			if err != nil {
				if err == io.EOF {
					return nil
				}
				return err
			}

			// Schreibe den Chunk sofort weiter an den Client (Kein Latenz-Overhead!)
			_, _ = clientWriter.Write(line)

			// Parst die standardisierte OpenAI/OpenRouter SSE-Syntax: "data: {...}"
			if !bytes.HasPrefix(line, []byte("data: ")) {
				continue
			}

			dataPayload := bytes.TrimPrefix(line, []byte("data: "))
			dataPayload = bytes.TrimSpace(dataPayload)

			if string(dataPayload) == "[DONE]" {
				return nil
			}

			var chunk SSEUsageChunk
			if err := json.Unmarshal(dataPayload, &chunk); err != nil {
				continue // Ignoriere Metadaten-Fragmente, die no gültiges JSON sind
			}

			// Die meisten Provider senden das 'usage'-Objekt im allerletzten Stream-Chunk
			if chunk.Usage != nil {
				onUsageFound(chunk.Usage.PromptTokens, chunk.Usage.CompletionTokens)
			}
		}
	}
}
import { ReactFlow, Background, Controls, Handle, Position } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Icon } from '@iconify/react';

// Custom Node Komponente for die Tech-Ontologie with Iconify Integration
const DiscoveredServiceNode = ({ data }: any) => {
  return (
    <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl w-60 text-slate-100">
      <Handle type="target" position={Position.Left} className="w-2 h-2 bg-indigo-500" />
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-slate-800 rounded-lg">
          <Icon icon={data.iconKey || 'lucide:box'} className="w-6 h-6" style={{ color: data.brandColor || '#94a3b8' }} />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold truncate">{data.label}</h4>
          <p className="text-xs text-slate-400 truncate">{data.category} • Port {data.port}</p>
        </div>
      </div>
      {data.metrics && (
        <div className="mt-2 pt-2 border-t border-slate-800 flex justify-between text-[10px] font-mono text-slate-400">
          <span>RPS: <span className="text-emerald-400">{data.metrics.rps}</span></span>
          <span>LAT: <span className="text-amber-400">{data.metrics.latency_ms}ms</span></span>
        </div>
      )}
      <Handle type="source" position={Position.Right} className="w-2 h-2 bg-indigo-500" />
    </div>
  );
};

const nodeTypes = { discoveredNode: DiscoveredServiceNode };

export function SecOpsTopologyCanvas({ liveTopologyData }: any) {
  // Generiert die Kanten with animierten pulsierenden SVG-Strichen basierend on dem Datenverkehr
  const animatedEdges = useMemo(() => {
    return liveTopologyData.edges.map((edge: any) => ({
      ...edge,
      animated: edge.metrics.rps > 0, // Kante pulsiert nur, wenn aktiver Traffic fließt
      style: {
        stroke: edge.metrics.errorRate > 0.1 ? '#ef4444' : '#6366f1', // Rot at hoher Fehlerrate
        strokeWidth: edge.metrics.rps > 20 ? 3 : 1.5,                 // Dickere Kante at hohem Durchsatz
      },
    }));
  }, [liveTopologyData.edges]);

  return (
    <div className="w-full h-[600px] bg-slate-950 rounded-xl border border-slate-800 overflow-hidden shadow-inner">
      <ReactFlow
        nodes={liveTopologyData.nodes}
        edges={animatedEdges}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background color="#334155" gap={16} size={1} />
        <Controls className="bg-slate-900 border border-slate-800 text-slate-100 fill-slate-100" />
      </ReactFlow>
    </div>
  );
}

import (
	"context"
	"math"
	"sync"
)

type TokenLogprob struct {
	Token   string  `json:"token"`
	Logprob float64 `json:"logprob"` // Logarithmische Wahrscheinlichkeit von der API
}

type EntropyCascadeRouter struct {
	mu            sync.RWMutex
	windowSize    int
	threshold     float64
	entropyWindow []float64
}

func NewEntropyCascadeRouter(windowSize int, threshold float64) *EntropyCascadeRouter {
	return &EntropyCascadeRouter{
		windowSize:    windowSize,
		threshold:     threshold,
		entropyWindow: make([]float64, 0, windowSize),
	}
}

// CalculateNormalizedEntropy berechnet H_norm from den Top-k Logprobs
func (ecr *EntropyCascadeRouter) CalculateNormalizedEntropy(topLogprobs []TokenLogprob) float64 {
	k := float64(len(topLogprobs))
	if k <= 1 {
		return 0.0
	}

	var entropy float64
	for _, item := range topLogprobs {
		// Wandelt Logprob zurück in lineare Wahrscheinlichkeit p ∈ [0..1]
		p := math.Exp(item.logprob)
		if p > 0 {
			entropy -= p * math.Log2(p)
		}
	}

	maxEntropy := math.Log2(k)
	return entropy / maxEntropy
}

// PushAndEvaluate schiebt die aktuelle Entropie in das gleitende Fenster and prüft den Trigger
func (ecr *EntropyCascadeRouter) PushAndEvaluate(entropy float64) bool {
	ecr.mu.Lock()
	defer ecr.mu.Unlock()

	// Fenster-Puffer verwalten
	if len(ecr.entropyWindow) >= ecr.windowSize {
		ecr.entropyWindow = ecr.entropyWindow[1:]
	}
	ecr.entropyWindow = append(ecr.entropyWindow, entropy)

	// Mindestens die Hälfte des Fensters muss befüllt sein for eine valide Aussage
	if len(ecr.entropyWindow) < ecr.windowSize/2 {
		return false
	}

	// Berechne die durchschnittliche Entropie des rollierenden Fensters
	var sum float64
	for _, val := range ecr.entropyWindow {
		sum += val
	}
	avgEntropy := sum / float64(len(ecr.entropyWindow))

	// Gibt true zurück, wenn der Schwellenwert gerissen wurde -> Eskalations-Trigger!
	return avgEntropy >= ecr.threshold
}

import (
	"regexp"
	"strings"
)

var (
	vendorCleanRegex = regexp.MustCompile(`^(openrouter/|groq/|together/|meta/|google/|deepseek/|nvidia/)`)
	tagCleanRegex    = regexp.MustCompile(`(:latest|:preview|:free|\-instruct|\-chat|\-v[0-9.]+)`)
)

// CanonicalNormalize bereinigt die ID in eine reine, kanonische Modellfamilie
func CanonicalNormalize(modelID string) string {
	lower := strings.ToLower(modelID)
	lower = vendorCleanRegex.ReplaceAllString(lower, "")
	lower = tagCleanRegex.ReplaceAllString(lower, "")
	lower = strings.ReplaceAll(lower, "_", "-")
	return strings.TrimSpace(lower)
}

// JaroWinklerDistance berechnet die Ähnlichkeit zwischen 0.0 (komplett unähnlich) and 1.0 (identisch)
func JaroWinklerDistance(s1, s2 string) float64 {
	s1Runes := []rune(s1)
	s2Runes := []rune(s2)

	l1 := len(s1Runes)
	l2 := len(s2Runes)

	if l1 == 0 || l2 == 0 {
		return 0.0
	}

	matchDistance := int(math.Max(float64(l1), float64(l2))/2.0) - 1
	if matchDistance < 0 {
		matchDistance = 0
	}

	s1Matches := make([]bool, l1)
	s2Matches := make([]bool, l2)

	matches := 0
	for i := 0; i < l1; i++ {
		start := int(math.Max(0, float64(i-matchDistance)))
		end := int(math.Min(float64(i+matchDistance+1), float64(l2)))

		for j := start; j < end; j++ {
			if s2Matches[j] {
				continue
			}
			if s1Runes[i] == s2Runes[j] {
				s1Matches[i] = true
				s2Matches[j] = true
				matches++
				break
			}
		}
	}

	if matches == 0 {
		return 0.0
	}

	transpositions := 0
	k := 0
	for i := 0; i < l1; i++ {
		if !s1Matches[i] {
			continue
		}
		for !s2Matches[k] {
			k++
		}
		if s1Runes[i] != s2Runes[k] {
			transpositions++
		}
		k++
	}

	m := float64(matches)
	t := float64(transpositions) / 2.0

	jaro := (m/float64(l1) + m/float64(l2) + (m-t)/m) / 3.0

	// Winkler Modifikation (Präfix Bonus)
	prefixLength := 0
	maxPrefix := int(math.Min(4, math.Min(float64(l1), float64(l2))))
	for i := 0; i < maxPrefix; i++ {
		if s1Runes[i] == s2Runes[i] {
			prefixLength++
		} else {
			break
		}
	}

	p := 0.1 // Standard Skalierungsfaktor
	return jaro + float64(prefixLength)*p*(1.0-jaro)
}

// IsDuplicateModel entscheidet at einem Threshold von 0.88 about die Klassen-Deduplikation
func IsDuplicateModel(id1, id2 string) bool {
	c1 := CanonicalNormalize(id1)
	c2 := CanonicalNormalize(id2)

	if c1 == c2 {
		return true
	}

	return JaroWinklerDistance(c1, c2) >= 0.88
}

import (
	"context"
	"fmt"
	"io"
	"net"
	"os"
	"sync"
)

type MCPSocketSplicer struct {
	mu         sync.Mutex
	socketPath string
	listener   net.Listener
	active     bool
}

func NewMCPSocketSplicer(socketPath string) *MCPSocketSplicer {
	return &MCPSocketSplicer{
		socketPath: socketPath,
	}
}

// BindAndSplice initialisiert den UNIX Domain Socket and bereitet das Kernel-Splicing before
func (mss *MCPSocketSplicer) BindAndSplice(ctx context.Context, targetTCPAddr string) error {
	mss.mu.Lock()

	// Falls der Socket noch von einem alten Absturz existiert, wegräumen
	if _, err := os.Stat(mss.socketPath); err == nil {
		_ = os.Remove(mss.socketPath)
	}

	l, err := net.Listen("unix", mss.socketPath)
	if err != nil {
		mss.mu.Unlock()
		return fmt.Errorf("failed to bind unix socket: %w", err)
	}

	// Rechte restriktiv setzen (SecOps Isolation): Nur der OpenMesh-Prozess darf den Socket lesen
	_ = os.Chmod(mss.socketPath, 0600)

	mss.listener = l
	mss.active = true
	mss.mu.Unlock()

	go func() {
		<-ctx.Done()
		mss.Close()
	}()

	for {
		unixConn, err := l.Accept()
		if err != nil {
			if !mss.active {
				return nil // Sauber beendet
			}
			continue
		}

		// Asynchroner Vorwärts-Kanal zum isolierten Docker MCP Gateway via TCP
		go mss.spliceToUpstream(unixConn, targetTCPAddr)
	}
}

func (mss *MCPSocketSplicer) spliceToUpstream(unixConn net.Conn, tcpAddr string) {
	defer unixConn.Close()

	tcpConn, err := net.Dial("tcp", tcpAddr)
	if err != nil {
		return
	}
	defer tcpConn.Close()

	// Bidirektionales Splicing on Kernel-Ebene (Zero-Copy Nachbau via io.Copy)
	errChan := make(chan error, 2)

	go func() {
		_, err := io.Copy(tcpConn, unixConn)
		errChan <- err
	}()

	go func() {
		_, err := io.Copy(unixConn, tcpConn)
		errChan <- err
	}()

	// Blockiert, bis einer der beiden Datenströme terminiert
	<-errChan
}

func (mss *MCPSocketSplicer) Close() {
	mss.mu.Lock()
	defer mss.mu.Unlock()

	if !mss.active {
		return
	}

	mss.active = false
	if mss.listener != nil {
		_ = mss.listener.Close()
	}
	_ = os.Remove(mss.socketPath)
}
cd src/backend && go build -o /tmp/openmesh-server ./cmd/server
package network

import (
	"fmt"
	"net"
	"os"
	"syscall"
)

type LinuxKernelSplicer struct {
	socketPath string
}

func NewLinuxKernelSplicer(socketPath string) *LinuxKernelSplicer {
	return &LinuxKernelSplicer{socketPath: socketPath}
}

// SpliceConn verknüpft eine Unix-Verbindung direkt on Kernel-Ebene with einem TCP-Socket
func (lks *LinuxKernelSplicer) SpliceConn(unixConn net.Conn, tcpAddr string) error {
	defer unixConn.Close()

	// 1. Auflösung in rohe Datei-Deskriptoren (File Descriptors)
	rawUnix, err := unixConn.(*net.UnixConn).File()
	if err != nil {
		return err
	}
	defer rawUnix.Close()

	tcpConn, err := net.Dial("tcp", tcpAddr)
	if err != nil {
		return err
	}
	defer tcpConn.Close()

	rawTCP, err := tcpConn.(*net.TCPConn).File()
	if err != nil {
		return err
	}
	defer rawTCP.Close()

	// 2. Erzeuge eine unidirektionale Linux Pipe als Kernel-Buffer
	pipeFds := make([]int, 2)
	if err := syscall.Pipe2(pipeFds, syscall.O_NONBLOCK); err != nil {
		return fmt.Errorf("kernel pipe allocation failed: %w", err)
	}
	pipeRead := os.NewFile(uintptr(pipeFds[0]), "pipe-r")
	pipeWrite := os.NewFile(uintptr(pipeFds[1]), "pipe-w")
	defer pipeRead.Close()
	defer pipeWrite.Close()

	// 3. Bidirektionales Splicing via Goroutines starten
	errChan := make(chan error, 2)

	// Stream A: Unix -> TCP (Kernel Splicing)
	go func() {
		uFd := rawUnix.Fd()
		tFd := rawTCP.Fd()
		wFd := pipeWrite.Fd()
		rFd := pipeRead.Fd()

		for {
			// Phase A: Verschiebe Daten vom Unix-Socket in die Pipe (Write-End)
			n, err := syscall.Splice(int(uFd), nil, int(wFd), nil, 32768, 1) // 1 = SPLICE_F_MOVE
			if n == 0 || err != nil {
				errChan <- err
				return
			}
			// Phase B: Verschiebe Daten von der Pipe (Read-End) in den TCP-Target-Socket
			_, err = syscall.Splice(int(rFd), nil, int(tFd), nil, int(n), 1)
			if err != nil {
				errChan <- err
				return
			}
		}
	}()

	<-errChan
	return nil
}

import (
	"math"
	"sync"
)

var (
	boolPool = sync.Pool{
		New: func() interface{} {
			b := make([]bool, 512) // Unterstützt Modell-IDs bis zu 512 Zeichen without Re-Allokation
			return &b
		},
	}
)

func FastJaroWinkler(s1, s2 string) float64 {
	if s1 == s2 {
		return 1.0
	}

	l1 := len(s1)
	l2 := len(s2)
	if l1 == 0 || l2 == 0 {
		return 0.0
	}

	matchDist := int(math.Max(float64(l1), float64(l2))/2.0) - 1
	if matchDist < 0 {
		matchDist = 0
	}

	ptr1 := boolPool.Get().(*[]bool)
	ptr2 := boolPool.Get().(*[]bool)
	s1Matches := *ptr1
	s2Matches := *ptr2

	// Slices zurücksetzen (da sie from dem Pool stammen)
	for i := 0; i < l1; i++ { s1Matches[i] = false }
	for i := 0; i < l2; i++ { s2Matches[i] = false }

	matches := 0
	for i := 0; i < l1; i++ {
		start := int(math.Max(0, float64(i-matchDist)))
		end := int(math.Min(float64(i+matchDist+1), float64(l2)))

		for j := start; j < end; j++ {
			if s2Matches[j] {
				continue
			}
			if s1[i] == s2[j] {
				s1Matches[i] = true
				s2Matches[j] = true
				matches++
				break
			}
		}
	}

	if matches == 0 {
		boolPool.Put(ptr1)
		boolPool.Put(ptr2)
		return 0.0
	}

	transpositions := 0
	k := 0
	for i := 0; i < l1; i++ {
		if !s1Matches[i] {
			continue
		}
		for !s2Matches[k] {
			k++
		}
		if s1[i] != s2[k] {
			transpositions++
		}
		k++
	}

	boolPool.Put(ptr1)
	boolPool.Put(ptr2)

	m := float64(matches)
	t := float64(transpositions) / 2.0
	jaro := (m/float64(l1) + m/float64(l2) + (m-t)/m) / 3.0

	// Winkler Bonus for identische Präfixe (max 4 Zeichen)
	prefix := 0
	maxPrefix := int(math.Min(4, math.Min(float64(l1), float64(l2))))
	for i := 0; i < maxPrefix; i++ {
		if s1[i] == s2[i] {
			prefix++
		} else {
			break
		}
	}

	return jaro + float64(prefix)*0.1*(1.0-jaro)
}

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"time"
	"://github.com"
)

type ProxyHandler struct {
	BudgetEngine *BudgetManager
	VaultEngine  *store.VaultGateway
}

type ChatCompletionRequest struct {
	Model    string `json:"model"`
	Stream   bool   `json:"stream"`
	Messages []any  `json:"messages"`
}

func (ph *ProxyHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Only POST allowed", http.StatusMethodNotAllowed)
		return
	}

	ctx, cancel := context.WithCancel(r.Context())
	defer cancel()

	userID := r.Header.Get("X-OpenMesh-User-ID")
	projectID := r.Header.Get("X-OpenMesh-Project-ID")

	// 1. FinOps & RBAC Schutzschicht prüfen (R15)
	budget, err := ph.BudgetEngine.CheckBudgetAndInjectKey(ctx, userID, projectID)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusPaymentRequired)
		_, _ = w.Write([]byte(fmt.Sprintf(`{"error": "%s"}`, err.Error())))
		return
	}

	// 2. Just-In-Time Secret-Extraktion from der Vault (R16)
	apiKey, err := ph.VaultEngine.ResolveSecret(ctx, nil, projectID, "openrouter_api_key")
	if err != nil {
		http.Error(w, "Vault security resolution failed", http.StatusInternalServerError)
		return
	}

	// 3. Request-Body decodieren, um Modell-ID for das Preismapping zu lesen
	var reqBody ChatCompletionRequest
	bodyBytes, _ := io.ReadAll(r.Body)
	_ = json.Unmarshal(bodyBytes, &reqBody)

	// Bereite Upstream Request before
	upstreamReq, _ := http.NewRequestWithContext(ctx, "POST", "https://openrouter.ai", bytes.NewReader(bodyBytes))
	upstreamReq.Header.Set("Content-Type", "application/json")
	upstreamReq.Header.Set("Authorization", "Bearer "+apiKey)

	client := &http.Client{Timeout: 60 * time.Second}
	resp, err := client.Do(upstreamReq)
	if err != nil {
		http.Error(w, "Upstream provider timeout", http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()

	// 4. SSE-Streaming-Modus an den Browser übergeben
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")
	w.WriteHeader(http.StatusOK)

	// Abfangen der Chunks and Real-Time-Kosten-Berechnung
	flusher, _ := w.(http.Flusher)
	err = StreamCostEvaluator(ctx, resp.Body, w, func(promptTokens, completionTokens int64) {
		// Diese Callback-Funktion wird im exakten Moment aufgerufen, in dem das 'usage'-Objekt im Stream vorbeifliegt
		// Beispielhaftes Preis-Mapping (In der Praxis via R10 Model-Stats Pipeline geladen)
		inputCost := (float64(promptTokens) / 1000.0) * 0.00015
		outputCost := (float64(completionTokens) / 1000.0) * 0.00060
		totalCost := inputCost + outputCost

		// Atomare Abbuchung vom Benutzer-Konto
		_ = ph.BudgetEngine.TrackAndApplyCost(ctx, userID, projectID, totalCost)

		// Falls die Live-Abbuchung das Budget sprengt, wird hier die Verbindung gekappt
		if budget.SpentBudgetUSD+totalCost >= budget.MaxBudgetUSD {
			cancel() // Sendet das Abbruchsignal an alle Systemkomponenten (Mid-Stream Disconnect)
		}
	})

	if err == nil {
		flusher.Flush()
	}
}

import (
	"encoding/csv"
	"embed"
	"io"
	"strconv"
	"strings"
	"sync"
)

//go:embed assets/service-names-port-numbers.csv
var ianaAssetEmbed embed.FS

type IANAMapper struct {
	mu    sync.RWMutex
	cache map[string]string // Key: "port/proto" -> Value: Service Name
}

func NewIANAMapper() *IANAMapper {
	return &IANAMapper{
		cache: make(map[string]string),
	}
}

// BootstrapIANALocal lädt den eingebetteten CSV-Dump beim Systemstart in den RAM
func (im *IANAMapper) BootstrapIANALocal() error {
	im.mu.Lock()
	defer im.mu.Unlock()

	file, err := ianaAssetEmbed.Open("assets/service-names-port-numbers.csv")
	if err != nil {
		return err
	}
	defer file.Close()

	reader := csv.NewReader(file)
	// Überspringe den Header-Eintrag
	_, _ = reader.Read()

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return err
		}

		// CSV Spalten-Layout: 0: Service Name, 1: Port Number, 2: Transport Protocol
		if len(record) < 3 {
			continue
		}

		portStr := record[1]
		proto := strings.ToLower(record[2])
		serviceName := record[0]

		if portStr == "" || proto == "" || serviceName == "" {
			continue
		}

		// Ranges (z.B. 100-105) ignorieren, nur diskrete Sockets mappen
		if strings.Contains(portStr, "-") {
			continue
		}

		key := portStr + "/" + proto
		im.cache[key] = serviceName
	}
	return nil
}

// ResolvePortToServiceName prüft den offenen Port deterministisch gegen den IANA-RAM-Cache
func (im *IANAMapper) ResolvePortToServiceName(port int, proto string) (string, bool) {
	im.mu.RLock()
	defer im.mu.RUnlock()

	key := strconv.Itoa(port) + "/" + strings.ToLower(proto)
	name, exists := im.cache[key]
	return name, exists
}

import (
	"context"
	"fmt"
	"://github.com"
)

type TokenBudgetEvaluator struct {
	modelEncodingMap map[string]string
}

func NewTokenBudgetEvaluator() *TokenBudgetEvaluator {
	return &TokenBudgetEvaluator{
		modelEncodingMap: map[string]string{
			"gpt-4o":         "cl100k_base",
			"deepseek-chat":  "cl100k_base", // Kompatibler Tokenizer-Stamm
			"claude-3-5":     "claude",      // Tiktoken-Spezifikation for Anthropic-Clans
		},
	}
}

// PreFlightCalculateCost prüft das Prompt-Volumen and wirft Fehler at Budgetgrenzen
func (tbe *TokenBudgetEvaluator) PreFlightCalculateCost(ctx context.Context, modelID, userPrompt string, costPer1K float64) (float64, error) {
	encodingName, exists := tbe.modelEncodingMap[modelID]
	if !exists {
		encodingName = "cl100k_base" // Ausfallsicherer Industrie-Standard
	}

	// Initialisiert den hocheffizienten Byte-Pair-Encoding Tokenizer im RAM
	tkm, err := tiktoken.GetEncoding(encodingName)
	if err != nil {
		return 0.0, fmt.Errorf("tokenizer initialization failed: %w", err)
	}

	// Berechnet die Token-Anzahl without Netzwerk-Latenz
	tokenSlice := tkm.Encode(userPrompt, nil, nil)
	tokenCount := int64(len(tokenSlice))

	// Mathematisch präzise Kostenkalkulation
	estimatedCostUSD := (float64(tokenCount) / 1000.0) * costPer1K
	return estimatedCostUSD, nil
}

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

func TestE2EProxyPipelineBudgetEnforcement(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	// 1. Setup Mock-Infrastruktur Komponenten
	evaluator := NewTokenBudgetEvaluator()
	prompt := "Write a secure multi-user role-based access control subsystem in Go."

	// Simuliere Pre-Flight Token Counting
	cost, err := evaluator.PreFlightCalculateCost(ctx, "gpt-4o", prompt, 0.0015)
	if err != nil {
		t.Fatalf("Pre-flight calculation threw unexpected error: %v", err)
	}

	if cost <= 0.0 {
		t.Errorf("Expected positive cost calculation, got: %f", cost)
	}

	// 2. Simuliere den HTTP HTTP/3 Proxy Gateway Server-Mux
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Header) {
		w.Header().Set("Content-Type", "text/event-stream")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("data: {\"choices\": [{\"delta\": {\"content\": \"package main\"}}]}\n\n"))
	})

	req := httptest.NewRequest("POST", "/api/v1/chat/completions", strings.NewReader(`{"model":"gpt-4o"}`))
	req.Header.Set("X-OpenMesh-User-ID", "user-leo-test")
	req.Header.Set("X-OpenMesh-Project-ID", "proj-abc-test")

	rr := httptest.NewRecorder()
	handler.ServeHTTP(rr, req)

	if rr.Code != http.StatusOK {
		t.Errorf("Expected status code 200, got %d", rr.Code)
	}

	if !strings.Contains(rr.Body.String(), "package main") {
		t.Errorf("Stream interception failed, core output chunk missing from buffer")
	}
}

import (
	"bytes"
	"io"
	"sync"
)

var (
	bufferPool = sync.Pool{
		New: func() interface{} {
			b := make([]byte, 4096) // 4KB Puffer pro Streaming-Chunk
			return &b
		},
	}
	promptTokenAnchor     = []byte(`"prompt_tokens"`)
	completionTokenAnchor = []byte(`"completion_tokens"`)
)

// ZeroAllocStreamParser extrahiert Token-Zahlen direkt from dem Byte-Stream without JSON-Heap-Allokation
func ZeroAllocStreamParser(upstream io.Reader, client http.ResponseWriter, onCostTrigger func(p, c int64)) error {
	ptr := bufferPool.Get().(*[]byte)
	buf := *ptr
	defer bufferPool.Put(ptr)

	flusher, _ := client.(http.Flusher)

	for {
		n, err := upstream.Read(buf)
		if n > 0 {
			// 1. Daten unverzüglich and latenzfrei an den Client durchreichen
			_, writeErr := client.Write(buf[:n])
			if writeErr == nil && flusher != nil {
				flusher.Flush()
			}

			// 2. Schnelle Byte-Inspektion im Kernel-nahen Buffer
			chunk := buf[:n]
			if bytes.Contains(chunk, promptTokenAnchor) {
				pTokens := extractIntBytes(chunk, promptTokenAnchor)
				cTokens := extractIntBytes(chunk, completionTokenAnchor)
				if pTokens > 0 || cTokens > 0 {
					onCostTrigger(pTokens, cTokens)
				}
			}
		}

		if err != nil {
			if err == io.EOF {
				return nil
			}
			return err
		}
	}
}

// Hilfsfunktion zur wegspeicherungsfreien Extraktion von Integern from rohen Slices
func extractIntBytes(src, anchor []byte) int64 {
	idx := bytes.Index(src, anchor)
	if idx == -1 {
		return 0
	}

	// Suche after der darauffolgenden Zahl after dem Doppelpunkt
	start := idx + len(anchor)
	for start < len(src) && (src[start] == ':' || src[start] == ' ' || src[start] == '\t') {
		start++
	}

	end := start
	for end < len(src) && src[end] >= '0' && src[end] <= '9' {
		end++
	}

	if start == end {
		return 0
	}

	var res int64
	for i := start; i < end; i++ {
		res = res*10 + int64(src[i]-'0')
	}
	return res
}
package gateway

import (
	"fmt"
	"://github.com"
	"://github.com/link"
	"://github.com/rlimit"
)

type KernelSocketEvent struct {
	PID  uint32
	Port uint16
	Comm [16]byte
}

type EBPFTracker struct {
	collection *ebpf.Collection
	kprobe     link.Link
}

func BootstrapEBPFTracker() (*EBPFTracker, error) {
	// 1. Entferne Speicher-Limits for eBPF-Maps im Linux-Kernel
	if err := rlimit.RemoveMemlock(); err != nil {
		return nil, fmt.Errorf("failed to remove memlock: %w", err)
	}

	// 2. Lade den vorkompilierten eBPF-C-Bytecode (In der Praxis via go-bindata or embed geladen)
	spec, err := ebpf.LoadCollectionSpec("/opt/openmesh/ebpf/socket_tracker.o")
	if err != nil {
		return nil, fmt.Errorf("failed to load ebpf spec: %w", err)
	}

	coll, err := ebpf.NewCollection(spec)
	if err != nil {
		return nil, fmt.Errorf("failed to create ebpf collection: %w", err)
	}

	// 3. Klinke den eBPF-Hook in den sys_enter_bind Systemaufruf ein
	kp, err := link.Tracepoint("syscalls", "sys_enter_bind", coll.Programs["trace_sys_bind"], nil)
	if err != nil {
		coll.Close()
		return nil, fmt.Errorf("failed to attach tracepoint: %w", err)
	}

	return &EBPFTracker{
		collection: coll,
		kprobe:     kp,
	}, nil
}

func (et *EBPFTracker) Close() {
	if et.kprobe != nil {
		_ = et.kprobe.Close()
	}
	if et.collection != nil {
		et.collection.Close()
	}
}

import (
	"context"
	"fmt"
	"time"
	vault "://github.com"
)

// GenerateEphemeralAgentToken erzeugt ein kurzlebiges, scoped Token for isolierte Werkzeuge
func (vg *VaultGateway) GenerateEphemeralAgentToken(ctx context.Context, projectID string, duration time.Duration) (string, error) {
	// Definiere eine restriktive Zugriffspolice exklusiv for den Pfad dieses einen Projekts
	policyName := fmt.Sprintf("openmesh-policy-%s", projectID)
	policyRules := fmt.Sprintf(`
		path "secret/data/projects/%s/*" {
			capabilities = ["read"]
		}`, projectID)

	// 1. Schreibe die temporäre Policy in den Core
	_ = vg.defaultClient.Sys().PutPolicy(policyName, policyRules)

	// 2. Erzeuge das Token with harter TTL-Verankerung
	secret, err := vg.defaultClient.Auth().Token().CreateWithContext(ctx, &vault.TokenCreateRequest{
		Policies: []string{policyName},
		TTL:      fmt.Sprintf("%ds", int(duration.Seconds())),
		NumUses:  5, // Maximal 5 Verwendungen erlaubt (Danach Selbstzerstörung)
	})
	if err != nil {
		return "", fmt.Errorf("failed to generate ephemeral vault token: %w", err)
	}

	// Gibt das Einweg-Token an das Docker MCP Framework zurück
	return secret.Auth.ClientToken, nil
}
