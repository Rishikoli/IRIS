import React from 'react';
import { FraudChainListItem } from '../services/api';
import Card, { CardContent, CardHeader, CardTitle } from './ui/Card';
import Skeleton from './ui/Skeleton';

interface Props {
  chains: FraudChainListItem[];
  onSelectChain: (chainId: string) => void;
  loading: boolean;
  selectedChainId?: string;
}

const FraudChainList: React.FC<Props> = ({ chains, onSelectChain, loading, selectedChainId }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Available Chains</CardTitle>
      </CardHeader>
      <CardContent>
        {loading && (
          <div className="space-y-2">
            {[...Array(5)].map((_, idx) => (
              <Skeleton key={idx} height={40} />
            ))}
          </div>
        )}
        {!loading && chains.length === 0 && (
          <p className="text-sm text-contrast-500">No fraud chains found.</p>
        )}
        {!loading && chains.length > 0 && (
          <ul className="space-y-2">
            {chains.map((chain) => (
              <li key={chain.id}>
                <button
                  onClick={() => onSelectChain(chain.id)}
                  className={`w-full text-left p-3 rounded-lg border transition-colors ${
                    selectedChainId === chain.id
                      ? 'bg-primary-50 border-primary-300 text-primary-800'
                      : 'bg-white hover:bg-contrast-50 border-contrast-200'
                  }`}
                >
                  <div className="font-semibold">{chain.name || `Chain ${chain.id}`}</div>
                  <div className="text-xs text-contrast-600">
                    {chain.node_count} nodes, {chain.edge_count} edges
                  </div>
                  <div className="text-xs text-contrast-400 mt-1">
                    Updated: {new Date(chain.updated_at).toLocaleString()}
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
};

export default FraudChainList;
