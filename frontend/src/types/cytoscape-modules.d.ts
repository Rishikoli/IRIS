declare module 'react-cytoscapejs' {
  import type { ComponentType } from 'react'
  import type { Core, Stylesheet, ElementDefinition, LayoutOptions } from 'cytoscape'

  interface CytoscapeComponentProps {
    elements?: ElementDefinition[] | { nodes: ElementDefinition[]; edges: ElementDefinition[] }
    stylesheet?: Stylesheet[] | any
    layout?: LayoutOptions | any
    style?: React.CSSProperties
    className?: string
    cy?: (cy: Core) => void
    wheelSensitivity?: number
  }

  const CytoscapeComponent: ComponentType<CytoscapeComponentProps>
  export default CytoscapeComponent
}

declare module 'cytoscape-fcose' {
  const ext: any
  export default ext
}

declare module 'cytoscape-dagre' {
  const ext: any
  export default ext
}
