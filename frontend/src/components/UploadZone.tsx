import { useCallback } from 'react';

type Props = {
  onFile: (file: File) => void;
};

const UploadZone = ({ onFile }: Props) => {
  const onChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) onFile(file);
    },
    [onFile],
  );

  return (
    <label className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-white p-6 hover:border-blue-500">
      <span className="text-sm text-gray-600">Kliknite pre nahratie RTG snímky</span>
      <input type="file" className="hidden" accept="image/*" onChange={onChange} />
    </label>
  );
};

export default UploadZone;
