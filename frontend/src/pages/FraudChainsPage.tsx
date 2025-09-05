import React, { useEffect, useState } from 'react';
import { fraudChainApi, FraudChain, FraudChainListItem } from '../services/api';
import FraudChainGraph from '../components/FraudChainGraph';
import Card, { CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import Toolbar from '../components/ui/Toolbar';
import Skeleton from '../components/ui/Skeleton';
import EmptyState from '../components/ui/EmptyState';
import FraudChainList from '../components/FraudChainList';

const FraudChainsPage: React.FC = () => {
  const [chains, setChains] = useState<FraudChainListItem[]>([]);
  const [selectedChain, setSelectedChain] = useState<FraudChain | null>(null);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingGraph, setLoadingGraph] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadChains = async () => {
    setLoadingList(true);
    setError(null);
    try {
      const { data } = await fraudChainApi.getChains({ limit: 100 });
      setChains(data || []);
      if (!selectedChain && data?.[0]?.id) {
        await handleSelectChain(data[0].id);
      }
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to load fraud chains');
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => {
    const fetchChains = async () => {
      setLoadingList(true);
      setError(null);
      try {
        const { data } = await fraudChainApi.getChains({ limit: 100 });
        setChains(data || []);
        if (data?.[0]?.id) {
          await handleSelectChain(data[0].id);
        }
      } catch (e: any) {
        setError(e?.response?.data?.detail || e?.message || 'Failed to load fraud chains');
      } finally {
        setLoadingList(false);
      }
    };
    void fetchChains();
  }, []);

  const handleSelectChain = async (chainId: string) => {
    setLoadingGraph(true);
    setError(null);
    try {
      const { data } = await fraudChainApi.getChain(chainId);
      setSelectedChain(data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Failed to load selected chain');
      setSelectedChain(null);
    } finally {
      setLoadingGraph(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-contrast-900">Fraud Chains</h1>
          <Toolbar dense className="bg-white border-contrast-200">
            <button
              className="px-3 py-1.5 rounded-lg bg-primary-600 text-white disabled:opacity-50"
              onClick={async () => {
                try {
                  await fraudChainApi.autoLink();
                } finally {
                  await loadChains();
                }
              }}
            >Rebuild Chains</button>
            <button
              className="px-3 py-1.5 rounded-lg border border-contrast-200"
              onClick={() => loadChains()}
            >Refresh</button>
          </Toolbar>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <div className="lg:col-span-2 space-y-4">
          <FraudChainList
            chains={chains}
            onSelectChain={handleSelectChain}
            loading={loadingList}
            selectedChainId={selectedChain?.id}
          />
        </div>
        <div className="lg:col-span-3">
          <Card className="bg-background-50">
            <CardHeader>
              <CardTitle>{selectedChain?.name || 'Selected Chain Details'}</CardTitle>
            </CardHeader>
            <CardContent>
              {loadingGraph && <Skeleton height={500} />}
              {error && <div className="p-3 text-sm text-danger-700 bg-danger-50 border border-danger-200 rounded">{error}</div>}
              {!loadingGraph && !error && selectedChain && (
                <FraudChainGraph chain={selectedChain} className="h-[70vh]" />
              )}
              {!loadingGraph && !error && !selectedChain && (
                <EmptyState title="No Chain Selected" description="Select a chain from the list to view its graph." />
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default FraudChainsPage;
