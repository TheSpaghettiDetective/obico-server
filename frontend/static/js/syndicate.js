const Themes = {
  Light: 'Light',
  Dark: 'Dark',
  System: 'System',
}

export const yumi = {
  // only light theme is supported for now
  colors: [
    {
      name: 'primary',
      values: {[Themes.Light]: '#078ED3', [Themes.Dark]: '#FFCC2E'},
    },
    {
      name: 'primary-hover',
      values: {[Themes.Light]: '#0B88C8', [Themes.Dark]: '#70EFDE'},
    },
    {
      name: 'primary-muted',
      values: {[Themes.Light]: '#24A8EC', [Themes.Dark]: '#018786'},
    },
    {
      name: 'on-primary',
      values: {[Themes.Light]: '#FFFFFF', [Themes.Dark]: '#001210'},
    },
    {
      name: 'secondary',
      values: {[Themes.Light]: '#28303A', [Themes.Dark]: '#EBEBEB'},
    },
    {
      name: 'secondary-hover',
      values: {[Themes.Light]: '#424A54', [Themes.Dark]: '#D0D0D0'},
    },
    {
      name: 'on-secondary',
      values: {[Themes.Light]: '#EBEBEB', [Themes.Dark]: '#28303A'},
    },
    {
      name: 'success',
      values: {[Themes.Light]: '#5CB85C', [Themes.Dark]: '#5CB85C'},
    },
    {
      name: 'success-hover',
      values: {[Themes.Light]: '#4CAE4C', [Themes.Dark]: '#4CAE4C'},
    },
    {
      name: 'on-success',
      values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#ffffff'},
    },
    {
      name: 'danger',
      values: {[Themes.Light]: '#D9534F', [Themes.Dark]: '#D9534F'},
    },
    {
      name: 'danger-hover',
      values: {[Themes.Light]: '#C2413D', [Themes.Dark]: '#C2413D'},
    },
    {
      name: 'on-danger',
      values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#ffffff'},
    },
    {
      name: 'warning',
      values: {[Themes.Light]: '#F0AD4E', [Themes.Dark]: '#F0AD4E'},
    },
    {
      name: 'warning-hover',
      values: {[Themes.Light]: '#DB9A3F', [Themes.Dark]: '#DB9A3F'},
    },
    {
      name: 'on-warning',
      values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#ffffff'},
    },
    {
      name: 'on-warning-2',
      values: {[Themes.Light]: '#000000', [Themes.Dark]: '#000000'},
    },
    {
      name: 'background',
      values: {[Themes.Light]: '#EBEBEB', [Themes.Dark]: '#212224'},
    },
    {
      name: 'surface-primary',
      values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#485B71'},
    },
    {
      name: 'surface-secondary',
      values: {[Themes.Light]: '#F5F5F5', [Themes.Dark]: '#000000'},
    },
    {
      name: 'overlay',
      values: {[Themes.Light]: '#F5F5F5CC', [Themes.Dark]: '#000000CC'},
    },
    {
      name: 'hover',
      values: {[Themes.Light]: '#66666613', [Themes.Dark]: '#FFFFFF13'},
    },
    {
      name: 'hover-accent',
      values: {[Themes.Light]: '#66666626', [Themes.Dark]: '#C9E0FA26'},
    },
    {
      name: 'divider',
      values: {[Themes.Light]: '#ABB6C2', [Themes.Dark]: '#6A7B8A'},
    },
    {
      name: 'divider-muted',
      values: {[Themes.Light]: '#ABB6C266', [Themes.Dark]: '#6A7B8A66'},
    },
    {
      name: 'text-primary',
      values: {[Themes.Light]: '#28303A', [Themes.Dark]: '#EBEBEB'},
    },
    {
      name: 'text-secondary',
      values: {[Themes.Light]: '#8A94A2', [Themes.Dark]: '#AAACB0'},
    },
    {
      name: 'text-help',
      values: {[Themes.Light]: '#4C9BE8', [Themes.Dark]: '#4C9BE8'},
    },

    {
      name: 'input-background',
      values: {[Themes.Light]: '#E2E8ED', [Themes.Dark]: '#42566B'},
    },
    {
      name: 'input-placeholder',
      values: {[Themes.Light]: '#28303A80', [Themes.Dark]: '#EBEBEB80'},
    },

    {
      name: 'table-accent',
      values: {[Themes.Light]: '#E3E3E3', [Themes.Dark]: '#283848'},
    },

    // Icon colors
    {
      name: 'icon-tunneling-1',
      values: {[Themes.Light]: '#4E5D6C', [Themes.Dark]: '#EAEAEA'},
    },
    {
      name: 'icon-tunneling-2',
      values: {[Themes.Light]: '#1D2935', [Themes.Dark]: '#CDCDCD'},
    },
  ],
}


export const biqu = {
  // only dark theme is supported for now
  colors: [
    {
      name: 'primary',
      values: {[Themes.Light]: '#3596f3', [Themes.Dark]: '#3596f3'},
    },
    {
      name: 'primary-hover',
      values: {[Themes.Light]: '#70EFDE', [Themes.Dark]: '#70EFDE'},
    },
    {
      name: 'primary-muted',
      values: {[Themes.Light]: '#018786', [Themes.Dark]: '#018786'},
    },
    {
      name: 'on-primary',
      values: {[Themes.Light]: '#001210', [Themes.Dark]: '#001210'},
    },
    {
      name: 'secondary',
      values: {[Themes.Light]: '#EBEBEB', [Themes.Dark]: '#EBEBEB'},
    },
    {
      name: 'secondary-hover',
      values: {[Themes.Light]: '#D0D0D0', [Themes.Dark]: '#D0D0D0'},
    },
    {
      name: 'on-secondary',
      values: {[Themes.Light]: '#28303A', [Themes.Dark]: '#28303A'},
    },
    {
      name: 'success',
      values: {[Themes.Light]: '#5CB85C', [Themes.Dark]: '#5CB85C'},
    },
    {
      name: 'success-hover',
      values: {[Themes.Light]: '#4CAE4C', [Themes.Dark]: '#4CAE4C'},
    },
    {
      name: 'on-success',
      values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#ffffff'},
    },
    {
      name: 'danger',
      values: {[Themes.Light]: '#D9534F', [Themes.Dark]: '#D9534F'},
    },
    {
      name: 'danger-hover',
      values: {[Themes.Light]: '#C2413D', [Themes.Dark]: '#C2413D'},
    },
    {
      name: 'on-danger',
      values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#ffffff'},
    },
    {
      name: 'warning',
      values: {[Themes.Light]: '#F0AD4E', [Themes.Dark]: '#F0AD4E'},
    },
    {
      name: 'warning-hover',
      values: {[Themes.Light]: '#DB9A3F', [Themes.Dark]: '#DB9A3F'},
    },
    {
      name: 'on-warning',
      values: {[Themes.Light]: '#ffffff', [Themes.Dark]: '#ffffff'},
    },
    {
      name: 'on-warning-2',
      values: {[Themes.Light]: '#000000', [Themes.Dark]: '#000000'},
    },
    {
      name: 'background',
      values: {[Themes.Light]: '#0a0c22', [Themes.Dark]: '#0a0c22'},
    },
    {
      name: 'surface-primary',
      values: {[Themes.Light]: '#20274f', [Themes.Dark]: '#20274f'},
    },
    {
      name: 'surface-secondary',
      values: {[Themes.Light]: '#0c1239', [Themes.Dark]: '#0c1239'},
    },
    {
      name: 'overlay',
      values: {[Themes.Light]: '#F5F5F5CC', [Themes.Dark]: '#F5F5F5CC'},
    },
    {
      name: 'hover',
      values: {[Themes.Light]: '#66666613', [Themes.Dark]: '#66666613'},
    },
    {
      name: 'hover-accent',
      values: {[Themes.Light]: '#66666626', [Themes.Dark]: '#66666626'},
    },
    {
      name: 'divider',
      values: {[Themes.Light]: '#6A7B8A', [Themes.Dark]: '#6A7B8A'},
    },
    {
      name: 'divider-muted',
      values: {[Themes.Light]: '#ABB6C266', [Themes.Dark]: '#ABB6C266'},
    },
    {
      name: 'text-primary',
      values: {[Themes.Light]: '#EBEBEB', [Themes.Dark]: '#EBEBEB'},
    },
    {
      name: 'text-secondary',
      values: {[Themes.Light]: '#AAACB0', [Themes.Dark]: '#AAACB0'},
    },
    {
      name: 'text-help',
      values: {[Themes.Light]: '#283848', [Themes.Dark]: '#283848'},
    },

    {
      name: 'input-background',
      values: {[Themes.Light]: '#42566B', [Themes.Dark]: '#42566B'},
    },
    {
      name: 'input-placeholder',
      values: {[Themes.Light]: '#28303A80', [Themes.Dark]: '#28303A80'},
    },

    {
      name: 'table-accent',
      values: {[Themes.Light]: '#E3E3E3', [Themes.Dark]: '#E3E3E3'},
    },

    // Icon colors
    {
      name: 'icon-tunneling-1',
      values: {[Themes.Light]: '#4E5D6C', [Themes.Dark]: '#4E5D6C'},
    },
    {
      name: 'icon-tunneling-2',
      values: {[Themes.Light]: '#1D2935', [Themes.Dark]: '#1D2935'},
    },
  ],
}
