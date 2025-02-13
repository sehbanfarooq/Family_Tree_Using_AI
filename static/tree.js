document.getElementById('toggle-form').addEventListener('click', function () {
    const form = document.getElementById('add-member-form');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
});

// Convert the members data into a hierarchical structure
const treeData = JSON.parse('{{ members | tojson | safe }}');

// Set up the SVG dimensions
const width = 960, height = 500;

const svg = d3.select("#tree-container")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", "translate(50, 50)");

const treeLayout = d3.tree().size([width - 200, height - 200]);

// Creating a hierarchy from the tree data
const root = d3.hierarchy({ name: "Root", children: treeData }, d => d.children);
treeLayout(root);

// Create the links (lines between nodes)
svg.selectAll("line.link")
    .data(root.links())
    .enter()
    .append("line")
    .classed("link", true)
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);

// Create the nodes (family members)
const nodes = svg.selectAll("g.node")
    .data(root.descendants())
    .enter()
    .append("g")
    .classed("node", true)
    .attr("transform", d => `translate(${d.x}, ${d.y})`);

nodes.append("circle")
    .attr("r", 10)
    .style("fill", "#4CAF50");

nodes.append("text")
    .attr("dy", -15)
    .attr("text-anchor", "middle")
    .text(d => d.data.name);



// Expand and collapse behavior for "Add Member" form
document.getElementById('toggle-add-form').addEventListener('click', function () {
    const formContainer = document.getElementById('add-member-form');
    if (formContainer.style.display === 'none' || formContainer.style.display === '') {
        formContainer.style.display = 'block';
        this.textContent = 'Close Form';
    } else {
        formContainer.style.display = 'none';
        this.textContent = 'Add New Family Member';
    }
});



// Handle form toggle for add member
document.getElementById('toggle-form-btn').addEventListener('click', function () {
    const form = document.getElementById('add-member-form');
    form.style.display = (form.style.display === 'block') ? 'none' : 'block';
});