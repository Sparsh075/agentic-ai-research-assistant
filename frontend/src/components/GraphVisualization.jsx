import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import API_URL from '../services/api';

const GraphVisualization = ({ topic, onTopicClick }) => {
    const svgRef = useRef();
    const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (topic) {
            fetchGraphData(topic);
        }
    }, [topic]);

    const fetchGraphData = async (topic) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_URL}/api/graph/visualize?topic=${encodeURIComponent(topic)}`);
            if (!response.ok) throw new Error('Failed to fetch graph data');
            const data = await response.json();
            setGraphData(data.data || { nodes: [], edges: [] });
        } catch (error) {
            console.error('Error fetching graph data:', error);
            setError(error.message);
            setGraphData({ nodes: [], edges: [] });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (graphData.nodes.length > 0 && svgRef.current) {
            renderGraph();
        }
    }, [graphData]);

    const renderGraph = () => {
        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove();

        const width = svg.node().clientWidth || 400;
        const height = svg.node().clientHeight || 400;

        svg.attr('width', width).attr('height', height);

        const { nodes, edges } = graphData;
        if (!nodes.length) return;

        // Create force simulation
        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(edges).id(d => d.id).distance(80))
            .force('charge', d3.forceManyBody().strength(-200))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(d => Math.sqrt(d.size) * 2 + 8));

        // Create links
        const link = svg.append('g')
            .selectAll('line')
            .data(edges)
            .enter().append('line')
            .attr('stroke', '#4b5563')
            .attr('stroke-opacity', 0.4)
            .attr('stroke-width', d => Math.sqrt(d.weight || 1) * 1.5);

        // Create nodes
        const node = svg.append('g')
            .selectAll('circle')
            .data(nodes)
            .enter().append('circle')
            .attr('r', d => Math.sqrt(d.size || 2) * 2.5 + 4)
            .attr('fill', d => d.color || '#3b82f6')
            .attr('stroke', '#fff')
            .attr('stroke-width', 1.5)
            .style('cursor', 'pointer')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended))
            .on('click', (event, d) => {
                if (onTopicClick) {
                    onTopicClick(d.name);
                }
            });

        // Add labels
        const labels = svg.append('g')
            .selectAll('text')
            .data(nodes)
            .enter().append('text')
            .text(d => (d.name || '').length > 12 ? (d.name || '').substring(0, 12) + '...' : d.name || '')
            .attr('font-size', '10px')
            .attr('text-anchor', 'middle')
            .attr('dy', '-16px')
            .attr('fill', '#e5e7eb')
            .style('pointer-events', 'none')
            .style('user-select', 'none');

        // Add tooltips
        node.append('title').text(d => d.name || 'Unknown');

        // Update positions
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

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96 text-gray-400">
                <div className="text-center">
                    <div className="animate-spin text-2xl mb-2">⏳</div>
                    Loading knowledge graph...
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-96 text-red-400">
                <div className="text-center">
                    <div className="text-xl mb-2">⚠️</div>
                    Error: {error}
                </div>
            </div>
        );
    }

    if (!topic) {
        return (
            <div className="flex items-center justify-center h-96 text-gray-400">
                <div className="text-center">
                    <div className="text-2xl mb-2">📊</div>
                    Select a topic to visualize the knowledge graph
                </div>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col">
            <h3 className="text-sm font-bold mb-2 text-blue-300">📊 {topic}</h3>
            <svg
                ref={svgRef}
                className="flex-1 border border-gray-700 rounded bg-gray-800"
                style={{ minHeight: '300px' }}
            ></svg>
            {graphData.nodes.length === 0 && !loading && (
                <div className="text-center text-gray-400 text-xs mt-2">
                    Click on nodes to explore topics
                </div>
            )}
        </div>
    );
};

export default GraphVisualization;