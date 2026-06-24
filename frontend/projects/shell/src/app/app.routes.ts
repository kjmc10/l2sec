import { Routes } from '@angular/router';
import { loadRemoteModule } from '@angular-architects/native-federation';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'dashboard',
  },
  {
    path: 'dashboard',
    loadChildren: () =>
      loadRemoteModule('nf-dashboard', './routes').then((m) => m.routes),
  },
  {
    path: 'targets',
    loadChildren: () =>
      loadRemoteModule({
        remoteName: 'nf-targets',
        exposedModule: './routes',
      }).then((m) => m.routes),
  },
  {
    path: 'runners',
    loadChildren: () =>
      loadRemoteModule({
        remoteName: 'nf-runners',
        exposedModule: './routes',
      }).then((m) => m.routes),
  },
  {
    path: 'findings',
    loadChildren: () =>
      loadRemoteModule('nf-findings', './routes').then((m) => m.routes),
  },
  {
    path: 'scan-jobs',
    loadChildren: () =>
      loadRemoteModule('nf-scan-jobs', './routes').then((m) => m.routes),
  },
  {
    path: '**',
    redirectTo: 'dashboard',
  },
];