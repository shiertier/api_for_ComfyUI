import { app } from "../../scripts/app.js";

const ext = {
    name: "ExportChenyuAPIFile",
    async init(app) {
      const exportButton = document.createElement('button');
      exportButton.textContent = "导出晨羽API文件";
      exportButton.onclick = async function () {
        try {
          const { output, workflow } = await app.graphToPrompt();
          const inputs = workflow.nodes
            .filter(node => node.type === 'PrimitiveNode')
            .map(node => {
              const widget = app.graph._nodes_by_id[node.id].widgets[0];
              const input = {
                id: node.id,
                type: node.outputs[0].type,
                name: node.outputs[0].widget.name,
                value: node.widgets_values[0],
                label: node.title || node.outputs[0].label,
                widget: widget.type
              };
              switch (input.widget) {
                case 'combo':
                case 'number':
                  input.options = widget.options;
                  break;
              }
              return input;
            });
  
          function saveToFile(content, filename) {
            const blob = new Blob([content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            setTimeout(() => {
              document.body.removeChild(a);
              URL.revokeObjectURL(url);
            }, 0);
          }
  
          saveToFile(
            JSON.stringify({
              prompt: output,
              chenyu_data: { inputs },
              extra_data: {
                extra_pnginfo: { workflow }
              }
            }),
            'workflow-chenyu.json'
          );
          alert('文件已成功导出！');
        } catch (error) {
          console.error('导出失败: ', error);
          alert('导出过程中发生错误');
        }
      };
  
      app.ui.menuContainer.appendChild(exportButton);
    }
  };
  
  app.registerExtension(ext);
  
