import React from "react";
import { A2UIPageSpec, ResolvedNode, ServerAction } from "../types";
import { resolveTree } from "./resolveTree";
import { DataModelContext, useDataModelState } from "../hooks/useDataModel";

import { ColumnBlock } from "../components/ColumnBlock";
import { RowBlock } from "../components/RowBlock";
import { TextBlock } from "../components/TextBlock";
import { CardBlock } from "../components/CardBlock";
import { ButtonBlock } from "../components/ButtonBlock";
import { CheckBoxBlock } from "../components/CheckBoxBlock";
import { IconBlock } from "../components/IconBlock";
import { DividerBlock } from "../components/DividerBlock";
import { DataTableBlock } from "../components/DataTableBlock";

interface A2UIRendererProps {
  spec: A2UIPageSpec;
  onAction: (action: ServerAction) => void;
  isLoading: boolean;
}

export function A2UIRenderer({ spec, onAction, isLoading }: A2UIRendererProps) {
  const { data, resolve, updatePath } = useDataModelState(spec.dataModel);
  const tree = resolveTree(spec.components, data);

  if (!tree) {
    return (
      <div className="error-banner" style={{ margin: "2rem auto", maxWidth: 900 }}>
        root 컴포넌트를 찾을 수 없습니다. components 배열에 id: "root"가 있는지 확인하세요.
      </div>
    );
  }

  return (
    <DataModelContext.Provider value={{ data, resolve, updatePath }}>
      <main className="a2ui-surface">
        {renderNode(tree, onAction, isLoading)}
      </main>
    </DataModelContext.Provider>
  );
}

function renderNode(
  node: ResolvedNode,
  onAction: (action: ServerAction) => void,
  isLoading: boolean
): React.ReactNode {
  const { component, children, scopePath } = node;

  const renderedChildren = children.map((child) =>
    renderNode(child, onAction, isLoading)
  );

  switch (component.component) {
    case "Column":
      return (
        <ColumnBlock key={component.id} gap={component.gap} align={component.align}>
          {renderedChildren}
        </ColumnBlock>
      );

    case "Row":
      return (
        <RowBlock key={component.id} gap={component.gap} align={component.align}>
          {renderedChildren}
        </RowBlock>
      );

    case "Text":
      return (
        <TextBlock
          key={component.id}
          text={component.text}
          variant={component.variant}
          color={component.color}
          scopePath={scopePath}
        />
      );

    case "Card":
      return (
        <CardBlock key={component.id}>
          {renderedChildren}
        </CardBlock>
      );

    case "Button":
      return (
        <ButtonBlock
          key={component.id}
          label={component.label}
          variant={component.variant}
          action={component.action}
          onAction={onAction}
          isLoading={isLoading}
        />
      );

    case "CheckBox":
      return (
        <CheckBoxBlock
          key={component.id}
          value={component.value}
          scopePath={scopePath}
        />
      );

    case "Icon":
      return (
        <IconBlock
          key={component.id}
          name={component.name || ""}
          size={component.size}
        />
      );

    case "Divider":
      return <DividerBlock key={component.id} />;

    case "DataTable":
      return (
        <DataTableBlock
          key={component.id}
          columns={component.columns}
          rows={component.rows}
        />
      );

    default:
      return (
        <div key={component.id} className="unknown-component">
          ⚠️ 알 수 없는 컴포넌트: {component.component}
        </div>
      );
  }
}
