import { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3';
import API_URL from '../services/api';

const GraphVisualization = ({ topic, graphData, onTopicClick }) => {
  const svgRef = useRef();
  const containerRef = useRef();
  const simulationRef = useRef(null);
  const [hoveredNode, setHoveredNode] = useState(null);

  // Clean up simulation on unmount
  useEffect(() => {
    return () => {
      if (simulationRef.current) {
        simulationRef.current.stop();
      }
    };
  }, []);

  useEffect(() => {
    if (graphData && graphData.nodes && graphData.nodes.length > 0 && svgRef.current) {
      renderGraph();
    }
  }, [graphData, topic]);

  const getNodeColor = useCallback((node) => {
    if (node.name === topic) return '#3b82f6'; // Active topic - blue
    if (node.depth === 0) return '#8b5cf6'; // Root - purple
    if (node.depth === 1) return '#06b6d4'; // Depth 1 - cyan
    if (node.depth === 2) return '#f59e0b'; // Depth 2 - amber
    return '#6b7280'; // Default - gray
  }, [topic]);

  const renderGraph = () => {
    if (simulationRef.current) {
      simulationRef.current.stop();
    }

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const container = containerRef.current;
    if (!container) return;

    const width = container.clientWidth || 600;
    const height = container.clientHeight || 260;

    svg.attr('width', width).attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`);

    const { nodes, links } = graphData;
    if (!nodes || !nodes.length) return;

    // Deep clone to avoid D3 mutation issues
    const nodesCopy = nodes.map(n => ({ ...n }));
    const linksCopy = (links || []).map(l => ({ ...l }));

    // Defs for glow filter
    const defs = svg.append('defs');
    
    const glowFilter = defs.append('filter')
      .attr('id', 'node-glow')
      .attr('x', '-50%').attr('y', '-50%')
      .attr('width', '200%').attr('height', '200%');
    
    glowFilter.append('feGaussianBlur')
      .attr('stdDeviation', '4')
      .attr('result', 'blur');
    
    const feMerge = glowFilter.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'blur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // Create zoom behavior
    const g = svg.append('g');
    
    const zoom = d3.zoom()
      .scaleExtent([0.3, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });
    
    svg.call(zoom);

    // Create simulation
    const simulation = d3.forceSimulation(nodesCopy)
      .force('link', d3.forceLink(linksCopy).id(d => d.id).distance(70).strength(0.5))
      .force('charge', d3.forceManyBody().strength(-180))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => getNodeRadius(d) + 4));

    simulationRef.current = simulation;

    // Draw links
    const link = g.append('g')
      .selectAll('line')
      .data(linksCopy)
      .enter().append('line')
      .attr('stroke', 'rgba(100, 130, 200, 0.15)')
      .attr('stroke-width', d => Math.max(0.5, Math.sqrt(d.weight || 1) * 0.8));

    // Draw nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(nodesCopy)
      .enter().append('circle')
      .attr('r', d => getNodeRadius(d))
      .attr('fill', d => getNodeColor(d))
      .attr('stroke', d => d.name === topic ? 'rgba(59, 130, 246, 0.6)' : 'rgba(255, 255, 255, 0.1)')
      .attr('stroke-width', d => d.name === topic ? 2.5 : 1)
      .attr('filter', d => d.name === topic ? 'url(#node-glow)' : 'none')
      .attr('opacity', 0.9)
      .style('cursor', 'pointer')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))
      .on('click', (event, d) => {
        event.stopPropagation();
        if (onTopicClick) onTopicClick(d.name);
      })
      .on('mouseenter', (event, d) => {
        setHoveredNode(d.name);
        d3.select(event.target)
          .transition().duration(150)
          .attr('r', getNodeRadius(d) + 3)
          .attr('stroke-width', 2.5)
          .attr('opacity', 1);
        
        // Highlight connected links
        link.transition().duration(150)
          .attr('stroke', l => 
            (l.source.id === d.id || l.target.id === d.id) 
              ? 'rgba(59, 130, 246, 0.4)' 
              : 'rgba(100, 130, 200, 0.08)'
          )
          .attr('stroke-width', l => 
            (l.source.id === d.id || l.target.id === d.id) 
              ? Math.max(1, Math.sqrt(l.weight || 1) * 1.5)
              : Math.max(0.3, Math.sqrt(l.weight || 1) * 0.5)
          );
      })
      .on('mouseleave', (event, d) => {
        setHoveredNode(null);
        d3.select(event.target)
          .transition().duration(200)
          .attr('r', getNodeRadius(d))
          .attr('stroke-width', d.name === topic ? 2.5 : 1)
          .attr('opacity', 0.9);
        
        link.transition().duration(200)
          .attr('stroke', 'rgba(100, 130, 200, 0.15)')
          .attr('stroke-width', l => Math.max(0.5, Math.sqrt(l.weight || 1) * 0.8));
      });

    // Draw labels
    const labels = g.append('g')
      .selectAll('text')
      .data(nodesCopy)
      .enter().append('text')
      .text(d => {
        const name = d.name || '';
        return name.length > 14 ? name.substring(0, 14) + '…' : name;
      })
      .attr('font-size', '9px')
      .attr('font-family', 'Inter, sans-serif')
      .attr('font-weight', d => d.name === topic ? '600' : '400')
      .attr('text-anchor', 'middle')
      .attr('dy', d => -(getNodeRadius(d) + 6))
      .attr('fill', d => d.name === topic ? '#93c5fd' : 'rgba(200, 210, 230, 0.6)')
      .style('pointer-events', 'none')
      .style('user-select', 'none');

    // Tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
      labels
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    });

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  };

  const getNodeRadius = (d) => {
    const base = Math.sqrt(d.size || 2) * 2 + 4;
    if (d.name === topic) return base + 3;
    return base;
  };

  if (!topic) {
    return (
      <div className="flex items-center justify-center h-full text-gray-600">
        <div className="text-center">
          <span className="text-2xl block mb-2 opacity-40">📊</span>
          <span className="text-xs">Select a topic to visualize</span>
        </div>
      </div>
    );
  }

  if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-600">
        <div className="text-center">
          <span className="text-2xl block mb-2 opacity-40">🔍</span>
          <span className="text-xs">Ask more questions to build the graph</span>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="graph-container w-full h-full relative">
      <svg ref={svgRef} className="w-full h-full" />
      {hoveredNode && (
        <div className="absolute bottom-3 left-3 glass-panel px-3 py-1.5 text-[11px] text-gray-300 pointer-events-none animate-fade-in">
          🔗 {hoveredNode}
        </div>
      )}
    </div>
  );
};

export default GraphVisualization;