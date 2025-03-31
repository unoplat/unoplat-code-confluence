// import React from 'react';
// import { useForm } from '@tanstack/react-form';
// import { Repository, RepositoryMetadata } from '../types';

// interface RepositoryMetadataFormProps {
//   repository: Repository;
//   onSubmit: (repository: Repository, metadata: RepositoryMetadata) => void;
//   onCancel: () => void;
// }

// const programmingLanguages = [
//   'JavaScript',
//   'TypeScript',
//   'Python',
//   'Java',
//   'C#',
//   'Go',
//   'Ruby',
//   'PHP',
//   'Rust',
//   'C++',
//   'Other',
// ];

// const packageManagers = [
//   'npm',
//   'yarn',
//   'pnpm',
//   'pip',
//   'pipenv',
//   'poetry',
//   'maven',
//   'gradle',
//   'nuget',
//   'cargo',
//   'composer',
//   'go mod',
//   'uv',
//   'other',
// ];

// export function RepositoryMetadataForm({
//   repository,
//   onSubmit,
//   onCancel,
// }: RepositoryMetadataFormProps): React.ReactElement {
//   const form = useForm({
//     defaultValues: {
//       codebaseFolder: '',
//       rootPackage: '',
//       programmingLanguage: '',
//       packageManager: '',
//     },
//     onSubmit: async ({ value }) => {
//       onSubmit(repository, value);
//     },
//   });
  
//   return (
//     <div className="bg-white shadow p-6 rounded-lg">
//       <div className="mb-6">
//         <h2 className="text-lg font-medium text-gray-900">
//           Repository Metadata: {repository.full_name}
//         </h2>
//         <p className="mt-1 text-sm text-gray-500">
//           Please provide additional information about your repository to proceed with the ingestion.
//         </p>
//       </div>
      
//       <form
//         onSubmit={(e) => {
//           e.preventDefault();
//           e.stopPropagation();
//           form.handleSubmit();
//         }}
//       >
//         <div className="space-y-6">
//           <form.Field
//             name="codebaseFolder"
//           >
//             {(field) => (
//               <div>
//                 <label htmlFor={field.name} className="block text-sm font-medium text-gray-700">
//                   Codebase Folder
//                 </label>
//                 <div className="mt-1">
//                   <input
//                     type="text"
//                     id={field.name}
//                     name={field.name}
//                     className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
//                     placeholder="e.g., src/"
//                     value={field.state.value}
//                     onChange={(e) => field.handleChange(e.target.value)}
//                   />
//                 </div>
//                 {field.state.meta.errors && (
//                   <p className="mt-2 text-sm text-red-600">{field.state.meta.errors.join(', ')}</p>
//                 )}
//                 <p className="mt-2 text-sm text-gray-500">
//                   Directory path in the ingestion pipeline where code is located.
//                 </p>
//               </div>
//             )}
//           </form.Field>
          
//           <form.Field
//             name="rootPackage"
//           >
//             {(field) => (
//               <div>
//                 <label htmlFor={field.name} className="block text-sm font-medium text-gray-700">
//                   Root Package
//                 </label>
//                 <div className="mt-1">
//                   <input
//                     type="text"
//                     id={field.name}
//                     name={field.name}
//                     className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
//                     placeholder="e.g., app.js, main.py"
//                     value={field.state.value}
//                     onChange={(e) => field.handleChange(e.target.value)}
//                   />
//                 </div>
//                 {field.state.meta.errors && (
//                   <p className="mt-2 text-sm text-red-600">{field.state.meta.errors.join(', ')}</p>
//                 )}
//                 <p className="mt-2 text-sm text-gray-500">
//                   The primary package or entry point of your application.
//                 </p>
//               </div>
//             )}
//           </form.Field>
          
//           <form.Field
//             name="programmingLanguage"
//           >
//             {(field) => (
//               <div>
//                 <label htmlFor={field.name} className="block text-sm font-medium text-gray-700">
//                   Programming Language
//                 </label>
//                 <div className="mt-1">
//                   <select
//                     id={field.name}
//                     name={field.name}
//                     className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
//                     value={field.state.value}
//                     onChange={(e) => field.handleChange(e.target.value)}
//                   >
//                     <option value="">Select a language</option>
//                     {programmingLanguages.map((lang) => (
//                       <option key={lang} value={lang}>
//                         {lang}
//                       </option>
//                     ))}
//                   </select>
//                 </div>
//                 {field.state.meta.errors && (
//                   <p className="mt-2 text-sm text-red-600">{field.state.meta.errors.join(', ')}</p>
//                 )}
//               </div>
//             )}
//           </form.Field>
          
//           <form.Field
//             name="packageManager"
//           >
//             {(field) => (
//               <div>
//                 <label htmlFor={field.name} className="block text-sm font-medium text-gray-700">
//                   Package Manager
//                 </label>
//                 <div className="mt-1">
//                   <select
//                     id={field.name}
//                     name={field.name}
//                     className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
//                     value={field.state.value}
//                     onChange={(e) => field.handleChange(e.target.value)}
//                   >
//                     <option value="">Select a package manager</option>
//                     {packageManagers.map((manager) => (
//                       <option key={manager} value={manager}>
//                         {manager}
//                       </option>
//                     ))}
//                   </select>
//                 </div>
//                 {field.state.meta.errors && (
//                   <p className="mt-2 text-sm text-red-600">{field.state.meta.errors.join(', ')}</p>
//                 )}
//               </div>
//             )}
//           </form.Field>
//         </div>
        
//         <div className="mt-6 flex justify-end space-x-3">
//           <button
//             type="button"
//             onClick={onCancel}
//             className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
//           >
//             Cancel
//           </button>
//           <button
//             type="submit"
//             className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
//           >
//             Submit
//           </button>
//         </div>
//       </form>
//     </div>
//   );
// } 